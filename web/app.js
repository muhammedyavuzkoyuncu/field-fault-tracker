const API_URL = "https://field-fault-tracker.onrender.com";

const TOKEN_KEY = "field_fault_tracker_token";
const USER_KEY = "field_fault_tracker_user";


/* =========================
   AUTHENTICATION
========================= */

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}


function getStoredUser() {
    const user = localStorage.getItem(USER_KEY);

    if (!user) {
        return null;
    }

    try {
        return JSON.parse(user);
    } catch (error) {
        return null;
    }
}


function saveSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}


function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}


function showLoginScreen() {
    document.getElementById("loginScreen").style.display = "flex";
    document.getElementById("appScreen").style.display = "none";
}


function showAppScreen() {
    document.getElementById("loginScreen").style.display = "none";
    document.getElementById("appScreen").style.display = "block";
}


function updateUserInformation(user) {
    document.getElementById("currentUsername").textContent =
        user.username;

    document.getElementById("currentRole").textContent =
        user.role;
}


/* =========================
   API HELPER
========================= */

async function apiFetch(url, options = {}) {

    const token = getToken();

    const headers = {
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_URL}${url}`,
        {
            ...options,
            headers
        }
    );

    if (response.status === 401) {
        clearSession();
        showLoginScreen();

        throw new Error("Oturum süresi doldu.");
    }

    return response;
}


/* =========================
   LOGIN
========================= */

async function loginUser(username, password) {

    const response = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Giriş başarısız."
        );
    }

    saveSession(
        data.access_token,
        data.user
    );

    updateUserInformation(data.user);

    showAppScreen();

    await initializeApplication();
}


async function handleLogin(event) {

    event.preventDefault();

    const username =
        document.getElementById("loginUsername").value.trim();

    const password =
        document.getElementById("loginPassword").value;

    const errorElement =
        document.getElementById("loginError");

    errorElement.style.display = "none";
    errorElement.textContent = "";

    try {

        await loginUser(
            username,
            password
        );

    } catch (error) {

        console.error("Login error:", error);

        errorElement.textContent =
            error.message;

        errorElement.style.display = "block";
    }
}


/* =========================
   LOGOUT
========================= */

function logout() {

    clearSession();

    document.getElementById("loginUsername").value = "";
    document.getElementById("loginPassword").value = "";

    showLoginScreen();
}


/* =========================
   CURRENT USER
========================= */

async function loadCurrentUser() {

    const response = await apiFetch(
        "/auth/me"
    );

    if (!response.ok) {
        throw new Error(
            "Kullanıcı bilgileri alınamadı."
        );
    }

    const user = await response.json();

    localStorage.setItem(
        USER_KEY,
        JSON.stringify(user)
    );

    updateUserInformation(user);

    return user;
}


/* =========================
   INITIALIZE APPLICATION
========================= */

async function initializeApplication() {

    const user = getStoredUser();

    if (!user) {
        showLoginScreen();
        return;
    }

    updateUserInformation(user);

    applyRolePermissions(user);

    try {

        await loadFaults();

        if (user.role === "ADMIN") {

            await loadUsers();

        }

    } catch (error) {

        console.error(
            "Application initialization error:",
            error
        );
    }
}


/* =========================
   ROLE PERMISSIONS
========================= */

function applyRolePermissions(user) {

    const adminSection =
        document.getElementById("adminSection");

    const systemSection =
        document.getElementById("systemSection");

    if (user.role === "ADMIN") {

        adminSection.style.display = "block";
        systemSection.style.display = "block";

    } else {

        adminSection.style.display = "none";
        systemSection.style.display = "none";
    }
}


/* =========================
   FAULTS
========================= */

async function loadFaults() {

    try {

        const response =
            await apiFetch("/faults");

        if (!response.ok) {

            throw new Error(
                "Arızalar yüklenemedi."
            );
        }

        const faults =
            await response.json();

        displayFaults(faults);

        updateDashboard(faults);

    } catch (error) {

        console.error(
            "Error loading faults:",
            error
        );

        document.getElementById(
            "faultTableBody"
        ).innerHTML = `
            <tr>
                <td colspan="7">
                    Arıza kayıtları yüklenemedi.
                </td>
            </tr>
        `;
    }
}


function displayFaults(faults) {

    const tableBody =
        document.getElementById(
            "faultTableBody"
        );

    tableBody.innerHTML = "";

    if (faults.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    Sistemde henüz arıza kaydı bulunmuyor.
                </td>
            </tr>
        `;

        return;
    }

    faults.forEach(fault => {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td>${fault.title || "-"}</td>

            <td>
                ${fault.equipment_name || "-"}
            </td>

            <td>
                ${fault.technician_name || "-"}
            </td>

            <td>
                ${fault.priority || "-"}
            </td>

            <td>
                ${fault.status || "-"}
            </td>

            <td>
                ${formatDate(fault.created_at)}
            </td>

            <td>
                <button
                    onclick="viewFault(${fault.id})">
                    Görüntüle
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });
}


function updateDashboard(faults) {

    const totalFaults =
        faults.length;

    const openFaults =
        faults.filter(
            fault => fault.status === "ACIK"
        ).length;

    const ongoingFaults =
        faults.filter(
            fault => fault.status === "DEVAM_EDIYOR"
        ).length;

    const closedFaults =
        faults.filter(
            fault => fault.status === "KAPALI"
        ).length;

    document.getElementById(
        "totalFaults"
    ).textContent = totalFaults;

    document.getElementById(
        "openFaults"
    ).textContent = openFaults;

    document.getElementById(
        "ongoingFaults"
    ).textContent = ongoingFaults;

    document.getElementById(
        "closedFaults"
    ).textContent = closedFaults;
}


/* =========================
   FAULT DETAIL
========================= */

async function viewFault(faultId) {

    try {

        const response =
            await apiFetch(
                `/faults/${faultId}`
            );

        if (!response.ok) {

            throw new Error(
                "Arıza detayları yüklenemedi."
            );
        }

        const fault =
            await response.json();

        if (
            fault.message ===
            "Fault not found"
        ) {

            alert("Arıza bulunamadı.");

            return;
        }

        document.getElementById(
            "detailTitle"
        ).textContent =
            fault.title || "-";

        document.getElementById(
            "detailDescription"
        ).textContent =
            fault.description || "-";

        document.getElementById(
            "detailStatus"
        ).textContent =
            fault.status || "-";

        document.getElementById(
            "detailPriority"
        ).textContent =
            fault.priority || "-";

        document.getElementById(
            "detailEquipment"
        ).textContent =
            fault.equipment_name || "-";

        document.getElementById(
            "detailCategory"
        ).textContent =
            fault.category_name || "-";

        document.getElementById(
            "detailTechnician"
        ).textContent =
            fault.technician_name || "-";

        document.getElementById(
            "detailCreatedAt"
        ).textContent =
            formatDate(fault.created_at);

        document.getElementById(
            "faultModal"
        ).style.display = "flex";

    } catch (error) {

        console.error(
            "Error loading fault details:",
            error
        );

        alert(
            "Arıza detayları yüklenemedi."
        );
    }
}


function closeFaultModal() {

    document.getElementById(
        "faultModal"
    ).style.display = "none";
}


/* =========================
   NEW FAULT
========================= */

function openNewFaultModal() {

    document.getElementById(
        "newFaultModal"
    ).style.display = "flex";

    loadFormData();
}


function closeNewFaultModal() {

    document.getElementById(
        "newFaultModal"
    ).style.display = "none";
}


async function loadFormData() {

    try {

        await Promise.all([
            loadEquipment(),
            loadCategories(),
            loadTechnicians()
        ]);

    } catch (error) {

        console.error(
            "Error loading form data:",
            error
        );

        alert(
            "Form bilgileri yüklenirken hata oluştu."
        );
    }
}


async function loadEquipment() {

    const response =
        await apiFetch(
            "/equipment"
        );

    if (!response.ok) {

        throw new Error(
            "Ekipmanlar yüklenemedi."
        );
    }

    const equipment =
        await response.json();

    const select =
        document.getElementById(
            "faultEquipment"
        );

    select.innerHTML = `
        <option value="">
            Ekipman seçiniz
        </option>
    `;

    equipment.forEach(item => {

        const option =
            document.createElement("option");

        option.value =
            item.id;

        option.textContent =
            `${item.equipment_code} - ${item.name}`;

        select.appendChild(option);
    });
}


async function loadCategories() {

    const response =
        await apiFetch(
            "/fault-categories"
        );

    if (!response.ok) {

        throw new Error(
            "Kategoriler yüklenemedi."
        );
    }

    const categories =
        await response.json();

    const select =
        document.getElementById(
            "faultCategory"
        );

    select.innerHTML = `
        <option value="">
            Kategori seçiniz
        </option>
    `;

    categories.forEach(category => {

        const option =
            document.createElement("option");

        option.value =
            category.id;

        option.textContent =
            `${category.category_code} - ${category.name}`;

        select.appendChild(option);
    });
}


async function loadTechnicians() {

    const response =
        await apiFetch(
            "/technicians"
        );

    if (!response.ok) {

        throw new Error(
            "Teknisyenler yüklenemedi."
        );
    }

    const technicians =
        await response.json();

    const select =
        document.getElementById(
            "faultTechnician"
        );

    select.innerHTML = `
        <option value="">
            Teknisyen seçiniz
        </option>
    `;

    technicians.forEach(technician => {

        const option =
            document.createElement("option");

        option.value =
            technician.id;

        option.textContent =
            technician.full_name;

        select.appendChild(option);
    });
}


async function saveNewFault() {

    const equipmentId =
        document.getElementById(
            "faultEquipment"
        ).value;

    const categoryId =
        document.getElementById(
            "faultCategory"
        ).value;

    const technicianId =
        document.getElementById(
            "faultTechnician"
        ).value;

    const title =
        document.getElementById(
            "faultTitle"
        ).value.trim();

    const description =
        document.getElementById(
            "faultDescription"
        ).value.trim();

    const priority =
        document.getElementById(
            "faultPriority"
        ).value;


    if (!equipmentId) {

        alert(
            "Lütfen ekipman seçiniz."
        );

        return;
    }


    if (!categoryId) {

        alert(
            "Lütfen kategori seçiniz."
        );

        return;
    }


    if (!technicianId) {

        alert(
            "Lütfen teknisyen seçiniz."
        );

        return;
    }


    if (!title) {

        alert(
            "Lütfen arıza başlığı giriniz."
        );

        return;
    }


    const faultData = {

        equipment_id:
            Number(equipmentId),

        category_id:
            Number(categoryId),

        technician_id:
            Number(technicianId),

        title:
            title,

        description:
            description,

        priority:
            priority
    };


    try {

        const response =
            await apiFetch(
                "/faults",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            faultData
                        )
                }
            );


        if (!response.ok) {

            const errorData =
                await response.json();

            throw new Error(
                errorData.detail ||
                "Arıza oluşturulamadı."
            );
        }


        await response.json();


        alert(
            "Arıza kaydı başarıyla oluşturuldu."
        );


        document.getElementById(
            "faultEquipment"
        ).value = "";

        document.getElementById(
            "faultCategory"
        ).value = "";

        document.getElementById(
            "faultTechnician"
        ).value = "";

        document.getElementById(
            "faultTitle"
        ).value = "";

        document.getElementById(
            "faultDescription"
        ).value = "";

        document.getElementById(
            "faultPriority"
        ).value = "ORTA";


        closeNewFaultModal();

        await loadFaults();

    } catch (error) {

        console.error(
            "Error creating fault:",
            error
        );

        alert(
            error.message ||
            "Arıza kaydı oluşturulurken hata oluştu."
        );
    }
}


/* =========================
   USERS - ADMIN
========================= */

async function loadUsers() {

    const user =
        getStoredUser();

    if (
        !user ||
        user.role !== "ADMIN"
    ) {
        return;
    }


    try {

        const response =
            await apiFetch(
                "/users"
            );

        if (!response.ok) {

            throw new Error(
                "Kullanıcılar yüklenemedi."
            );
        }

        const users =
            await response.json();

        displayUsers(users);

    } catch (error) {

        console.error(
            "Error loading users:",
            error
        );

        document.getElementById(
            "userTableBody"
        ).innerHTML = `
            <tr>
                <td colspan="5">
                    Kullanıcılar yüklenemedi.
                </td>
            </tr>
        `;
    }
}


function displayUsers(users) {

    const tableBody =
        document.getElementById(
            "userTableBody"
        );

    tableBody.innerHTML = "";


    users.forEach(user => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${user.username}
            </td>

            <td>
                ${user.email}
            </td>

            <td>
                ${user.role}
            </td>

            <td>
                ${formatDate(user.created_at)}
            </td>

            <td>
                ${
                    user.username === "admin"
                    ? "-"
                    : `
                        <button
                            onclick="deleteUser(${user.id})">
                            Sil
                        </button>
                    `
                }
            </td>
        `;


        tableBody.appendChild(row);
    });
}


function openNewUserModal() {

    document.getElementById(
        "newUserModal"
    ).style.display = "flex";
}


function closeNewUserModal() {

    document.getElementById(
        "newUserModal"
    ).style.display = "none";
}


async function saveNewUser() {

    const username =
        document.getElementById(
            "newUsername"
        ).value.trim();

    const email =
        document.getElementById(
            "newUserEmail"
        ).value.trim();

    const password =
        document.getElementById(
            "newUserPassword"
        ).value;

    const role =
        document.getElementById(
            "newUserRole"
        ).value;


    if (!username || !email || !password) {

        alert(
            "Lütfen tüm alanları doldurunuz."
        );

        return;
    }


    if (password.length < 8) {

        alert(
            "Şifre en az 8 karakter olmalıdır."
        );

        return;
    }


    try {

        const response =
            await apiFetch(
                "/users",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            username,
                            email,
                            password,
                            role
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Kullanıcı oluşturulamadı."
            );
        }


        alert(
            "Kullanıcı başarıyla oluşturuldu."
        );


        document.getElementById(
            "newUsername"
        ).value = "";

        document.getElementById(
            "newUserEmail"
        ).value = "";

        document.getElementById(
            "newUserPassword"
        ).value = "";

        document.getElementById(
            "newUserRole"
        ).value = "TECHNICIAN";


        closeNewUserModal();

        await loadUsers();

    } catch (error) {

        console.error(
            "Error creating user:",
            error
        );

        alert(
            error.message ||
            "Kullanıcı oluşturulamadı."
        );
    }
}


async function deleteUser(userId) {

    const confirmed =
        confirm(
            "Bu kullanıcıyı silmek istediğinize emin misiniz?"
        );

    if (!confirmed) {
        return;
    }


    try {

        const response =
            await apiFetch(
                `/users/${userId}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Kullanıcı silinemedi."
            );
        }


        alert(
            "Kullanıcı silindi."
        );


        await loadUsers();

    } catch (error) {

        console.error(
            "Error deleting user:",
            error
        );

        alert(
            error.message ||
            "Kullanıcı silinemedi."
        );
    }
}


/* =========================
   DATABASE TEST
========================= */

async function testDatabase() {

    const resultElement =
        document.getElementById(
            "systemResult"
        );


    resultElement.textContent =
        "Veritabanı bağlantısı test ediliyor...";


    try {

        const response =
            await apiFetch(
                "/db-test"
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Veritabanı testi başarısız."
            );
        }


        resultElement.textContent =
            `Veritabanı bağlantısı başarılı. Plant sayısı: ${data.plant_count}`;

    } catch (error) {

        console.error(
            "Database test error:",
            error
        );

        resultElement.textContent =
            error.message ||
            "Veritabanı bağlantısı başarısız.";
    }
}


/* =========================
   DATE
========================= */

function formatDate(dateString) {

    if (!dateString) {
        return "-";
    }

    const date =
        new Date(dateString);

    return date.toLocaleString(
        "tr-TR"
    );
}


/* =========================
   EVENT LISTENERS
========================= */

document.getElementById(
    "loginForm"
).addEventListener(
    "submit",
    handleLogin
);


document.getElementById(
    "logoutButton"
).addEventListener(
    "click",
    logout
);


document.getElementById(
    "closeModalButton"
).addEventListener(
    "click",
    closeFaultModal
);


document.getElementById(
    "closeModalButtonBottom"
).addEventListener(
    "click",
    closeFaultModal
);


document.getElementById(
    "faultModal"
).addEventListener(
    "click",
    function (event) {

        if (event.target === this) {
            closeFaultModal();
        }

    }
);


document.getElementById(
    "newFaultButton"
).addEventListener(
    "click",
    openNewFaultModal
);


document.getElementById(
    "closeNewFaultModalButton"
).addEventListener(
    "click",
    closeNewFaultModal
);


document.getElementById(
    "cancelNewFaultButton"
).addEventListener(
    "click",
    closeNewFaultModal
);


document.getElementById(
    "newFaultModal"
).addEventListener(
    "click",
    function (event) {

        if (event.target === this) {
            closeNewFaultModal();
        }

    }
);


document.getElementById(
    "saveNewFaultButton"
).addEventListener(
    "click",
    saveNewFault
);


document.getElementById(
    "newUserButton"
).addEventListener(
    "click",
    openNewUserModal
);


document.getElementById(
    "closeNewUserModalButton"
).addEventListener(
    "click",
    closeNewUserModal
);


document.getElementById(
    "cancelNewUserButton"
).addEventListener(
    "click",
    closeNewUserModal
);


document.getElementById(
    "newUserModal"
).addEventListener(
    "click",
    function (event) {

        if (event.target === this) {
            closeNewUserModal();
        }

    }
);


document.getElementById(
    "saveNewUserButton"
).addEventListener(
    "click",
    saveNewUser
);


document.getElementById(
    "dbTestButton"
).addEventListener(
    "click",
    testDatabase
);


/* =========================
   START APPLICATION
========================= */

async function startApplication() {

    const token =
        getToken();

    if (!token) {

        showLoginScreen();

        return;
    }


    try {

        const user =
            await loadCurrentUser();

        applyRolePermissions(user);

        showAppScreen();

        await initializeApplication();

    } catch (error) {

        console.error(
            "Session validation error:",
            error
        );

        clearSession();

        showLoginScreen();
    }
}


startApplication();