(() => {
  // Si ya hay sesión activa, saltar directo a Empleados
  if (getSession()) {
    window.location.href = "empleados.html";
    return;
  }

  const roleOptions = document.querySelectorAll(".role-option");
  const rolInput = document.getElementById("rol-input");
  roleOptions.forEach((opt) => {
    opt.addEventListener("click", () => {
      roleOptions.forEach((o) => o.classList.remove("active"));
      opt.classList.add("active");
      rolInput.value = opt.dataset.rol;
    });
  });

  const form = document.getElementById("login-form");
  const errorBox = document.getElementById("login-error");
  const submitBtn = document.getElementById("login-submit");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.remove("show");
    submitBtn.disabled = true;
    submitBtn.textContent = "Ingresando…";

    const payload = {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
      rol: rolInput.value,
    };

    try {
      const res = await api.login(payload);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "No fue posible iniciar sesión");

      setSession(data.access_token, {
        username: data.username,
        nombre: data.nombre,
        rol: data.rol,
      });
      window.location.href = "empleados.html";
    } catch (err) {
      errorBox.textContent = err.message || "Usuario o contraseña incorrectos";
      errorBox.classList.add("show");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Ingresar";
    }
  });
})();
