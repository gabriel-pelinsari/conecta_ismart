import mockNotifications from "../mocks/notifications";

function simulateDelay(result, delay = 250) {
  return new Promise((resolve) => setTimeout(() => resolve(result), delay));
}

export const notificationApi = {
  async list() {
    return simulateDelay(mockNotifications);
  },

  async markAsRead(notificationId) {
    const updated = mockNotifications.map((n) =>
      n.id === notificationId ? { ...n, is_read: true } : n
    );
    return simulateDelay(updated.find((n) => n.id === notificationId));
  },
};

export default notificationApi;
