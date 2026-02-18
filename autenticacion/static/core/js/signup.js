const formConfig = {
    turista: [
        { label: "Nombres *", type: "text", placeholder: "Juan" },
        { label: "Apellidos *", type: "text", placeholder: "Pérez" },
        { label: "Edad *", type: "number", placeholder: "25" },
        { label: "N° Identidad *", type: "text", placeholder: "1234567890" },
        { label: "Correo Electrónico *", type: "email", placeholder: "usuario@ejemplo.com" },
        { label: "Contraseña *", type: "password", placeholder: "••••••••" },
        { label: "Confirmación de Contraseña *", type: "password", placeholder: "••••••••" }
    ],
    agencia: [
        { label: "Nombre de la Agencia *", type: "text", placeholder: "Aventuras Colombia Tours" },
        { label: "Correo Electrónico *", type: "email", placeholder: "agencia@ejemplo.com" },
        { label: "Ubicación *", type: "text", placeholder: "Calle 100 # 15-20, Bogotá" },
        { label: "Número Telefónico *", type: "tel", placeholder: "+57 300 123 4567" },
        { label: "Contraseña *", type: "password", placeholder: "••••••••" },
        { label: "Confirmación de Contraseña *", type: "password", placeholder: "••••••••" }
    ],
    proveedor: [
        { label: "Nombre de Empresa *", type: "text", placeholder: "Equipos de Aventura SA" },
        { label: "Correo Electrónico *", type: "email", placeholder: "proveedor@ejemplo.com" },
        { label: "Teléfono *", type: "tel", placeholder: "+57 300 987 6543" },
        { label: "Contraseña *", type: "password", placeholder: "••••••••" }
        // Nota: Según la imagen de criterios, proveedor no listaba explícitamente "Confirmar Contraseña", 
        // pero se puede agregar si se requiere consistencia. Aquí sigo la lista estricta.
    ]
};

function setForm(type) {
    // 1. Actualizar estilos de los botones (Pestañas)
    const buttons = ['turista', 'agencia', 'proveedor'];
    buttons.forEach(btn => {
        const element = document.getElementById(`btn-${btn}`);
        if (btn === type) {
            // Estilo Activo
            element.className = "flex-1 flex items-center justify-center gap-2 bg-white text-gray-900 shadow-sm py-2 px-4 rounded-lg font-semibold text-sm transition-all border border-gray-200";
            element.classList.remove('text-gray-500', 'hover:bg-gray-50');
        } else {
            // Estilo Inactivo
            element.className = "flex-1 flex items-center justify-center gap-2 text-gray-500 hover:text-gray-700 py-2 px-4 rounded-lg font-medium text-sm transition-all hover:bg-gray-50";
        }
    });

    // 2. Actualizar descripción
    const descriptions = {
        turista: "Complete el formulario para registrarse como Turista.",
        agencia: "Registre su Agencia. El sistema validará que el nombre no exista previamente.",
        proveedor: "Complete la información de su empresa proveedora."
    };
    document.getElementById('form-description').innerText = descriptions[type];

    // 3. Renderizar campos del formulario
    const formContainer = document.getElementById('dynamic-form');
    formContainer.innerHTML = ''; // Limpiar anterior
    
    // Reiniciar animación
    formContainer.classList.remove('fade-in');
    void formContainer.offsetWidth; // Trigger reflow
    formContainer.classList.add('fade-in');

    formConfig[type].forEach(field => {
        const div = document.createElement('div');
        div.innerHTML = `
            <label class="block text-xs font-bold text-gray-700 mb-1 ml-1">${field.label}</label>
            <input type="${field.type}" placeholder="${field.placeholder}" class="w-full px-4 py-3 rounded-lg bg-input border-transparent focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition text-sm text-gray-700 placeholder-gray-400">
        `;
        formContainer.appendChild(div);
    });
}

// Inicializar con Turista por defecto
setForm('turista');