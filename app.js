async function viewFault(faultId) {

    try {

        const response = await fetch(
            `${API_URL}/faults/${faultId}`
        );

        if (!response.ok) {
            throw new Error("Fault details could not be loaded.");
        }

        const fault = await response.json();

        if (fault.message === "Fault not found") {
            alert("Arıza bulunamadı.");
            return;
        }

        alert(
            `Arıza Detayı\n\n` +
            `ID: ${fault.id}\n` +
            `Başlık: ${fault.title}\n` +
            `Açıklama: ${fault.description || "-"}\n` +
            `Durum: ${fault.status}\n` +
            `Öncelik: ${fault.priority}\n` +
            `Ekipman: ${fault.equipment_name || "-"}\n` +
            `Kategori: ${fault.category_name || "-"}\n` +
            `Teknisyen: ${fault.technician_name || "-"}`
        );

    } catch (error) {

        console.error("Error loading fault details:", error);

        alert("Arıza detayları yüklenemedi.");
    }
}