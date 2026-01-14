/**
 * Aplicação principal do Todoist
 * Gerencia autenticação, tarefas e interface do usuário
 */

const API_URL = 'http://localhost:8000';

// Estado da aplicação
const appState = {
    token: localStorage.getItem('token'),
    currentUser: null,
    tasks: [],
    editingTaskId: null
};

// Elementos do DOM
const elements = {
    authSection: document.getElementById('auth-section'),
    appSection: document.getElementById('app-section'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    showRegister: document.getElementById('show-register'),
    showLogin: document.getElementById('show-login'),
    loginFormElement: document.getElementById('login-form-element'),
    registerFormElement: document.getElementById('register-form-element'),
    logoutBtn: document.getElementById('logout-btn'),
    userName: document.getElementById('user-name'),
    taskForm: document.getElementById('task-form'),
    taskTitle: document.getElementById('task-title'),
    taskDescription: document.getElementById('task-description'),
    tasksList: document.getElementById('tasks-list'),
    emptyState: document.getElementById('empty-state'),
    totalTasks: document.getElementById('total-tasks'),
    completedTasks: document.getElementById('completed-tasks'),
    editModal: document.getElementById('edit-modal'),
    closeModal: document.getElementById('close-modal'),
    cancelEdit: document.getElementById('cancel-edit'),
    editTaskForm: document.getElementById('edit-task-form'),
    editTaskId: document.getElementById('edit-task-id'),
    editTaskTitle: document.getElementById('edit-task-title'),
    editTaskDescription: document.getElementById('edit-task-description'),
    toast: document.getElementById('toast')
};

/**
 * Exibe uma notificação toast
 */
function showToast(message, type = 'success') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

/**
 * Faz uma requisição à API
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (appState.token && !options.skipAuth) {
        headers['Authorization'] = `Bearer ${appState.token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(data?.detail || 'Erro na requisição');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Salva o token de autenticação
 */
function saveToken(token) {
    appState.token = token;
    localStorage.setItem('token', token);
}

/**
 * Remove o token de autenticação
 */
function clearToken() {
    appState.token = null;
    appState.currentUser = null;
    localStorage.removeItem('token');
}

/**
 * Alterna entre formulários de login e registro
 */
function toggleAuthForms() {
    elements.showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        elements.loginForm.style.display = 'none';
        elements.registerForm.style.display = 'block';
    });

    elements.showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        elements.registerForm.style.display = 'none';
        elements.loginForm.style.display = 'block';
    });
}

/**
 * Registra um novo usuário
 */
async function registerUser(username, email, password) {
    try {
        await apiRequest('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password }),
            skipAuth: true
        });

        showToast('Conta criada com sucesso! Faça login para continuar.', 'success');
        elements.registerForm.style.display = 'none';
        elements.loginForm.style.display = 'block';
        elements.registerFormElement.reset();
    } catch (error) {
        showToast(error.message || 'Erro ao criar conta', 'error');
    }
}

/**
 * Faz login do usuário
 */
async function loginUser(username, password) {
    try {
        const data = await apiRequest('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            skipAuth: true
        });

        saveToken(data.access_token);
        await loadCurrentUser();
        showAppSection();
        showToast(`Bem-vindo, ${username}!`, 'success');
    } catch (error) {
        showToast('Usuário ou senha incorretos', 'error');
    }
}

/**
 * Carrega os dados do usuário atual
 */
async function loadCurrentUser() {
    try {
        const user = await apiRequest('/api/auth/me');
        appState.currentUser = user;
        elements.userName.textContent = user.username;
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        logout();
    }
}

/**
 * Faz logout do usuário
 */
function logout() {
    clearToken();
    appState.tasks = [];
    showAuthSection();
    showToast('Você saiu da conta', 'success');
}

/**
 * Exibe a seção de autenticação
 */
function showAuthSection() {
    elements.authSection.style.display = 'flex';
    elements.appSection.style.display = 'none';
}

/**
 * Exibe a seção principal do app
 */
function showAppSection() {
    elements.authSection.style.display = 'none';
    elements.appSection.style.display = 'block';
    loadTasks();
}

/**
 * Carrega todas as tarefas do usuário
 */
async function loadTasks() {
    try {
        const tasks = await apiRequest('/api/tasks');
        appState.tasks = tasks;
        renderTasks();
        updateTasksStats();
    } catch (error) {
        showToast('Erro ao carregar tarefas', 'error');
    }
}

/**
 * Cria uma nova tarefa
 */
async function createTask(title, description) {
    try {
        const task = await apiRequest('/api/tasks', {
            method: 'POST',
            body: JSON.stringify({ title, description })
        });

        appState.tasks.push(task);
        renderTasks();
        updateTasksStats();
        elements.taskForm.reset();
        showToast('Tarefa criada com sucesso!', 'success');
    } catch (error) {
        showToast('Erro ao criar tarefa', 'error');
    }
}

/**
 * Atualiza uma tarefa existente
 */
async function updateTask(taskId, updates) {
    try {
        const updatedTask = await apiRequest(`/api/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });

        const index = appState.tasks.findIndex(t => t.id === taskId);
        if (index !== -1) {
            appState.tasks[index] = updatedTask;
        }

        renderTasks();
        updateTasksStats();
        showToast('Tarefa atualizada com sucesso!', 'success');
    } catch (error) {
        showToast('Erro ao atualizar tarefa', 'error');
    }
}

/**
 * Deleta uma tarefa
 */
async function deleteTask(taskId) {
    if (!confirm('Tem certeza que deseja excluir esta tarefa?')) {
        return;
    }

    try {
        await apiRequest(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        appState.tasks = appState.tasks.filter(t => t.id !== taskId);
        renderTasks();
        updateTasksStats();
        showToast('Tarefa excluída com sucesso!', 'success');
    } catch (error) {
        showToast('Erro ao excluir tarefa', 'error');
    }
}

/**
 * Alterna o status de conclusão de uma tarefa
 */
async function toggleTaskCompletion(taskId) {
    const task = appState.tasks.find(t => t.id === taskId);
    if (!task) return;

    await updateTask(taskId, { is_completed: !task.is_completed });
}

/**
 * Formata a data de criação da tarefa
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `${diffMins} min atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays}d atrás`;

    return date.toLocaleDateString('pt-BR');
}

/**
 * Renderiza a lista de tarefas
 */
function renderTasks() {
    elements.tasksList.innerHTML = '';

    if (appState.tasks.length === 0) {
        elements.emptyState.style.display = 'block';
        return;
    }

    elements.emptyState.style.display = 'none';

    // Ordena tarefas: não concluídas primeiro, depois por data de criação
    const sortedTasks = [...appState.tasks].sort((a, b) => {
        if (a.is_completed !== b.is_completed) {
            return a.is_completed ? 1 : -1;
        }
        return new Date(b.created_at) - new Date(a.created_at);
    });

    sortedTasks.forEach(task => {
        const taskElement = createTaskElement(task);
        elements.tasksList.appendChild(taskElement);
    });
}

/**
 * Cria o elemento HTML de uma tarefa
 */
function createTaskElement(task) {
    const taskDiv = document.createElement('div');
    taskDiv.className = `task-item ${task.is_completed ? 'completed' : ''}`;

    taskDiv.innerHTML = `
        <div class="task-content">
            <input
                type="checkbox"
                class="task-checkbox"
                ${task.is_completed ? 'checked' : ''}
                data-task-id="${task.id}"
            >
            <div class="task-details">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">Criada ${formatDate(task.created_at)}</div>
            </div>
        </div>
        <div class="task-actions">
            <button class="btn btn-edit" data-task-id="${task.id}">Editar</button>
            <button class="btn btn-delete" data-task-id="${task.id}">Excluir</button>
        </div>
    `;

    return taskDiv;
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Atualiza as estatísticas de tarefas
 */
function updateTasksStats() {
    const total = appState.tasks.length;
    const completed = appState.tasks.filter(t => t.is_completed).length;

    elements.totalTasks.textContent = `${total} ${total === 1 ? 'tarefa' : 'tarefas'}`;
    elements.completedTasks.textContent = `${completed} ${completed === 1 ? 'concluída' : 'concluídas'}`;
}

/**
 * Abre o modal de edição
 */
function openEditModal(taskId) {
    const task = appState.tasks.find(t => t.id === taskId);
    if (!task) return;

    appState.editingTaskId = taskId;
    elements.editTaskId.value = taskId;
    elements.editTaskTitle.value = task.title;
    elements.editTaskDescription.value = task.description || '';
    elements.editModal.classList.add('active');
}

/**
 * Fecha o modal de edição
 */
function closeEditModal() {
    appState.editingTaskId = null;
    elements.editModal.classList.remove('active');
    elements.editTaskForm.reset();
}

/**
 * Configura os event listeners
 */
function setupEventListeners() {
    // Autenticação
    elements.registerFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        await registerUser(username, email, password);
    });

    elements.loginFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        await loginUser(username, password);
    });

    elements.logoutBtn.addEventListener('click', logout);

    // Nova tarefa
    elements.taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = elements.taskTitle.value.trim();
        const description = elements.taskDescription.value.trim();

        if (!title) {
            showToast('O título é obrigatório', 'error');
            return;
        }

        await createTask(title, description);
    });

    // Delegação de eventos para tarefas
    elements.tasksList.addEventListener('click', async (e) => {
        const target = e.target;

        // Toggle checkbox
        if (target.classList.contains('task-checkbox')) {
            const taskId = parseInt(target.dataset.taskId);
            await toggleTaskCompletion(taskId);
        }

        // Botão editar
        if (target.classList.contains('btn-edit')) {
            const taskId = parseInt(target.dataset.taskId);
            openEditModal(taskId);
        }

        // Botão deletar
        if (target.classList.contains('btn-delete')) {
            const taskId = parseInt(target.dataset.taskId);
            await deleteTask(taskId);
        }
    });

    // Modal de edição
    elements.closeModal.addEventListener('click', closeEditModal);
    elements.cancelEdit.addEventListener('click', closeEditModal);

    elements.editModal.addEventListener('click', (e) => {
        if (e.target === elements.editModal) {
            closeEditModal();
        }
    });

    elements.editTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const taskId = parseInt(elements.editTaskId.value);
        const title = elements.editTaskTitle.value.trim();
        const description = elements.editTaskDescription.value.trim();

        if (!title) {
            showToast('O título é obrigatório', 'error');
            return;
        }

        await updateTask(taskId, { title, description });
        closeEditModal();
    });
}

/**
 * Inicializa a aplicação
 */
async function initApp() {
    toggleAuthForms();
    setupEventListeners();

    if (appState.token) {
        try {
            await loadCurrentUser();
            showAppSection();
        } catch (error) {
            clearToken();
            showAuthSection();
        }
    } else {
        showAuthSection();
    }
}

// Inicia a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initApp);
