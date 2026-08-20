const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function parseErrorMessage(data, status, defaultText) {
  let msg = data?.detail || data?.message || defaultText;
  if (Array.isArray(msg)) {
    msg = msg.map((e) => e.msg || JSON.stringify(e)).join(', ');
  }
  if (status === 401 && !data?.detail) return 'Authentication failed. Please check your credentials.';
  if (status === 403 && !data?.detail) return 'Access denied. You do not own this farm or device.';
  if (status === 404 && !data?.detail) return 'Requested resource or sensor reading not found.';
  if (status === 422 && !data?.detail) return 'Request validation failed. Check input values.';
  if (status === 503 && !data?.detail) return 'Backend service unavailable.';
  return msg;
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
  } catch {
    throw new ApiError(
      'Cannot reach the backend at 127.0.0.1:8000. Ensure server is running: uvicorn src.api.main:app --reload',
      0
    );
  }

  if (!response.ok) {
    let data = null;
    try {
      data = await response.json();
    } catch {
      // JSON parse fallback
    }
    const errorMsg = parseErrorMessage(data, response.status, response.statusText || 'An error occurred');
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
      'Cannot reach the backend at 127.0.0.1:8000. Start the server with: uvicorn src.api.main:app --reload',
      0
    );
  }

  if (!response.ok) {
    let data = null;
    try {
      data = await response.json();
    } catch {
      // fallback
    }
    const errorMsg = parseErrorMessage(data, response.status, 'Incorrect email or password');
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

export async function getSensorRecentApi() {
  return apiFetch('/sensor/recent');
}

export async function getDevicesApi() {
  return apiFetch('/device/');
}

export async function getAnalyticsApi() {
  return apiFetch('/analytics/overview');
}

export async function getRecommendationHistoryApi() {
  return apiFetch('/recommendation/history');
}

export async function getAlertsApi() {
  return apiFetch('/alerts/');
}

export async function controlDeviceApi(deviceId, command, duration_seconds = null) {
  return apiFetch(`/device/${deviceId}/control`, {
    method: 'POST',
    body: JSON.stringify({ command, duration_seconds }),
  });
}

