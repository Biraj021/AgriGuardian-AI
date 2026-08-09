const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('agriguardian_token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new ApiError(
      'Cannot reach the backend. Make sure the FastAPI server is running on port 8000.',
      0
    );
  }

  if (!response.ok) {
    let errorMsg = 'An error occurred';
    try {
      const data = await response.json();
      errorMsg = data.detail || data.message || errorMsg;
      if (Array.isArray(errorMsg)) {
        errorMsg = errorMsg.map((e) => e.msg || JSON.stringify(e)).join(', ');
      }
    } catch {
      errorMsg = response.statusText || errorMsg;
    }
    throw new ApiError(errorMsg, response.status);
  }

  return response.json();
}

export async function loginApi(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  let response;
  try {
    response = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
  } catch {
    throw new ApiError(
      'Cannot reach the backend. Start the server with: uvicorn src.api.main:app --reload',
      0
    );
  }

  if (!response.ok) {
    let errorMsg = 'Incorrect email or password';
    try {
      const data = await response.json();
      errorMsg = data.detail || errorMsg;
    } catch {
      errorMsg = response.statusText || errorMsg;
    }
    throw new ApiError(errorMsg, response.status);
  }

  return response.json();
}

export async function registerApi(email, password, role = 'farmer') {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, role }),
  });
}

export async function getMeApi() {
  return apiFetch('/auth/me');
}

export async function getFarmsApi() {
  return apiFetch('/farm/');
}

export async function getDashboardApi() {
  return apiFetch('/dashboard/');
}

export async function getIrrigationRecommendationApi(inputs) {
  return apiFetch('/recommendation/irrigation', {
    method: 'POST',
    body: JSON.stringify(inputs),
  });
}

export async function getWeatherApi() {
  return apiFetch('/weather/current');
}

export async function getMarketApi() {
  return apiFetch('/market/prices');
}
