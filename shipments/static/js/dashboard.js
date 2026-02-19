// Dashboard JavaScript - Shipment Management System
// Handles map interactions, location picking, and shipment CRUD operations

let senderMap, receiverMap, statusMap, mapPickerMap;
let senderMarker, receiverMarker, statusMarker, pickerMarker;
let currentPickerType = null;
let selectedLocation = null;

const DEFAULT_CENTER = [30.0444, 31.2357]; // القاهرة
const DEFAULT_ZOOM = 10;

// =======================================================
// 🗺️ وظائف الخرائط الأساسية والتهيئة 
// =======================================================

function initLeafletMap(mapId, initialLat, initialLng, clickHandler) {
    let mapInstance;

    // إزالة الخريطة القديمة لتجنب تراكب الخرائط عند إعادة الفتح
    const mapElement = document.getElementById(mapId);
    if (mapElement && mapElement._leaflet_id !== undefined) {
        try {
            // تحقق من وجود الخريطة أولا قبل محاولة الإزالة
            if (L.DomUtil.get(mapId)._leaflet_id) {
                L.map(mapId).remove();
            }
        } catch (e) { /* ignore */ }
    }

    try {
        mapInstance = L.map(mapId).setView([initialLat, initialLng], DEFAULT_ZOOM);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(mapInstance);

        if (clickHandler) {
            mapInstance.on('click', clickHandler);
        }

        // الحل لظهور الخريطة في الـ Modal: Invalidating Size
        setTimeout(() => {
            mapInstance.invalidateSize();
        }, 100);

        return mapInstance;
    } catch (error) {
        console.error(`Error initializing map ${mapId}:`, error);
        return null;
    }
}

function initSenderMap() {
    // استخدم initLeafletMap لإنشاء الخريطة بدلاً من L.map مباشرة
    senderMap = initLeafletMap('senderMap', DEFAULT_CENTER[0], DEFAULT_CENTER[1]);
}

function initReceiverMap() {
    receiverMap = initLeafletMap('receiverMap', DEFAULT_CENTER[0], DEFAULT_CENTER[1]);
}

function initStatusMap(lat = DEFAULT_CENTER[0], lng = DEFAULT_CENTER[1]) {
    // تهيئة خريطة تحديث الحالة
    statusMap = initLeafletMap('statusMap', lat, lng, async function (e) {
        const { lat, lng } = e.latlng;
        updateStatusMarker(lat, lng);
    });
}

function updateMapMarker(map, markerRefName, color, lat, lng, addressId, latId, lngId, title) {
    let currentMarker;
    if (markerRefName === 'senderMarker') currentMarker = senderMarker;
    else if (markerRefName === 'receiverMarker') currentMarker = receiverMarker;

    if (currentMarker) {
        map.removeLayer(currentMarker);
    }

    const customIcon = L.icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const newMarker = L.marker([lat, lng], { icon: customIcon }).addTo(map);

    // هذا الجزء لم يعد ضرورياً هنا، يتم تحديد العنوان في الـ Picker Modal
    // const address = await getAddressFromCoordinates(lat, lng); 
    const address = document.getElementById(addressId).value;

    if (address) {
        newMarker.bindPopup(`<b>${title}</b><br>${address}`).openPopup();
    } else {
        newMarker.bindPopup(`<b>${title}</b>`).openPopup();
    }

    document.getElementById(latId).value = lat.toFixed(6);
    document.getElementById(lngId).value = lng.toFixed(6);

    if (markerRefName === 'senderMarker') senderMarker = newMarker;
    else if (markerRefName === 'receiverMarker') receiverMarker = newMarker;
}

function updateStatusMarker(lat, lng) {
    if (statusMarker) {
        statusMap.removeLayer(statusMarker);
    }

    const icon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    statusMarker = L.marker([lat, lng], { icon: icon }).addTo(statusMap);
    statusMarker.bindPopup('<b>الموقع الحالي</b>').openPopup();

    document.getElementById('statusLat').value = lat.toFixed(6);
    document.getElementById('statusLng').value = lng.toFixed(6);
}


// =======================================================
// 📌 Map Picker Functions
// =======================================================

function openMapPicker(type) {
    currentPickerType = type;
    selectedLocation = null;

    const title = type === 'sender' ? 'اختر موقع المرسل' : 'اختر موقع المستلم';
    document.getElementById('mapPickerTitle').textContent = title;
    document.getElementById('selectedLocationInfo').style.display = 'none';
    document.getElementById('confirmLocationBtn').disabled = true;

    const modalElement = document.getElementById('mapPickerModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener('shown.bs.modal', function () {
        setTimeout(() => {
            initMapPicker();
        }, 100);
    }, { once: true });
}

function initMapPicker() {
    let initialLat = DEFAULT_CENTER[0];
    let initialLng = DEFAULT_CENTER[1];

    // إزالة الخريطة القديمة لتجنب التراكب
    if (mapPickerMap) {
        mapPickerMap.remove();
        mapPickerMap = null;
    }

    mapPickerMap = L.map('mapPicker').setView([initialLat, initialLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapPickerMap);

    mapPickerMap.on('click', async function (e) {
        await handleMapClick(e.latlng.lat, e.latlng.lng);
    });

    setTimeout(() => mapPickerMap.invalidateSize(), 100);
}

async function handleMapClick(lat, lng) {
    if (pickerMarker) {
        mapPickerMap.removeLayer(pickerMarker);
    }

    const iconColor = currentPickerType === 'sender' ? 'blue' : 'green';
    const customIcon = L.icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${iconColor}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    pickerMarker = L.marker([lat, lng], { icon: customIcon }).addTo(mapPickerMap);

    const address = await getAddressFromCoordinates(lat, lng);

    selectedLocation = {
        lat: lat,
        lng: lng,
        address: address || 'عنوان غير معروف'
    };

    document.getElementById('selectedAddress').textContent = selectedLocation.address;
    document.getElementById('selectedCoords').textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    document.getElementById('selectedLocationInfo').style.display = 'block';
    document.getElementById('confirmLocationBtn').disabled = false;

    pickerMarker.bindPopup(`<b>${selectedLocation.address}</b>`).openPopup();
}

function confirmLocation() {
    if (!selectedLocation) return;

    const lat = selectedLocation.lat;
    const lng = selectedLocation.lng;
    const address = selectedLocation.address;

    if (currentPickerType === 'sender') {
        document.getElementById('senderAddress').value = address;
        document.getElementById('senderLat').value = lat.toFixed(6);
        document.getElementById('senderLng').value = lng.toFixed(6);
        // يجب أن نضمن تهيئة الخريطة الصغيرة إذا لم يتم تهيئتها بعد
        if (!senderMap) initSenderMap();
        updateMapMarker(senderMap, 'senderMarker', 'blue', lat, lng, 'senderAddress', 'senderLat', 'senderLng', 'موقع المرسل');
    } else {
        document.getElementById('receiverAddress').value = address;
        document.getElementById('receiverLat').value = lat.toFixed(6);
        document.getElementById('receiverLng').value = lng.toFixed(6);
        // يجب أن نضمن تهيئة الخريطة الصغيرة إذا لم يتم تهيئتها بعد
        if (!receiverMap) initReceiverMap();
        updateMapMarker(receiverMap, 'receiverMarker', 'green', lat, lng, 'receiverAddress', 'receiverLat', 'receiverLng', 'موقع المستلم');
    }

    calculateDistanceAndPrice();
    bootstrap.Modal.getInstance(document.getElementById('mapPickerModal')).hide();
}

async function searchLocation() {
    const query = document.getElementById('mapSearch').value.trim();
    if (!query) return;

    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&accept-language=ar`
        );
        const data = await response.json();

        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);

            mapPickerMap.setView([lat, lng], 15);
            await handleMapClick(lat, lng);
        } else {
            alert('لم يتم العثور على المكان.');
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

// =======================================================
// 📊 Calculations (Distance & Price)
// =======================================================

async function getAddressFromCoordinates(lat, lng) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1&accept-language=ar`
        );
        const data = await response.json();
        return data.display_name || 'عنوان غير معروف';
    } catch (error) {
        return null;
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // km
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c);
}

function calculatePrice() {
    const basePrice = 50;
    const weightRate = 10;
    const distanceRate = 2;

    const weight = parseFloat(document.getElementById('weight').value) || 0;
    const distance = parseFloat(document.getElementById('distance').value) || 0;

    const price = basePrice + (weight * weightRate) + (distance * distanceRate);

    document.getElementById('price').value = price.toFixed(2);
    return price;
}

function calculateDistanceAndPrice() {
    const senderLat = parseFloat(document.getElementById('senderLat').value);
    const senderLng = parseFloat(document.getElementById('senderLng').value);
    const receiverLat = parseFloat(document.getElementById('receiverLat').value);
    const receiverLng = parseFloat(document.getElementById('receiverLng').value);

    if (senderLat && senderLng && receiverLat && receiverLng) {
        const distance = calculateDistance(senderLat, senderLng, receiverLat, receiverLng);
        document.getElementById('distance').value = distance.toFixed(2);
        calculatePrice();
    } else {
        document.getElementById('distance').value = '0.00';
        calculatePrice();
    }
}

// =======================================================
// 🚚 Shipment API/Data Functions
// =======================================================

function getStatusText(status) {
    const statusMap = {
        'pending': 'قيد الانتظار',
        'picked_up': 'تم الاستلام',
        'in_transit': 'في الطريق',
        'out_for_delivery': 'خارج للتوصيل',
        'delivered': 'تم التسليم',
        'cancelled': 'ملغي'
    };
    return statusMap[status] || status;
}

function displayShipments(shipments) {
    const container = document.getElementById('shipmentsContainer');

    if (shipments.length === 0) {
        container.innerHTML = '<div class="alert alert-info text-center"><i class="fas fa-info-circle me-1"></i> لا توجد شحنات مسجلة حتى الآن.</div>';
        return;
    }

    let html = '<div class="table-responsive"><table class="table table-hover align-middle">';
    html += '<thead class="table-light"><tr><th>رقم التتبع</th><th>المرسل</th><th>المستلم</th><th>الوزن/المسافة</th><th>الحالة</th><th>الإجراءات</th></tr></thead><tbody>';

    shipments.forEach(shipment => {
        html += `<tr>
            <td><strong>#${shipment.tracking_number}</strong></td>
            <td>${shipment.sender_name} <br><small class="text-muted">${shipment.sender_address.substring(0, 30)}...</small></td>
            <td>${shipment.receiver_name} <br><small class="text-muted">${shipment.receiver_address.substring(0, 30)}...</small></td>
            <td>${shipment.weight} كجم / ${shipment.distance_km || 'N/A'} كم</td>
            <td><span class="status-badge status-${shipment.status}">${getStatusText(shipment.status)}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="openUpdateStatus(${shipment.id})">
                    <i class="fas fa-edit"></i> تحديث الحالة
                </button>
            </td>
        </tr>`;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

async function loadShipments() {
    try {
        const response = await axios.get('/api/shipments/');
        displayShipments(response.data);
    } catch (error) {
        console.error('Error loading shipments:', error);
        document.getElementById('shipmentsContainer').innerHTML =
            '<div class="alert alert-danger text-center"><i class="fas fa-times-circle me-1"></i> حدث خطأ في تحميل الشحنات. (تأكد من إعداد API)</div>';
    }
}

async function submitShipment() {
    // جلب البيانات من النموذج
    const data = {
        sender_name: document.getElementById('senderName').value,
        sender_address: document.getElementById('senderAddress').value,
        sender_lat: document.getElementById('senderLat').value || null,
        sender_lng: document.getElementById('senderLng').value || null,
        receiver_name: document.getElementById('receiverName').value,
        receiver_address: document.getElementById('receiverAddress').value,
        receiver_email: document.getElementById('receiverEmail').value,
        receiver_lat: document.getElementById('receiverLat').value || null,
        receiver_lng: document.getElementById('receiverLng').value || null,
        weight: parseFloat(document.getElementById('weight').value) || 0,
        distance_km: document.getElementById('distance').value ? parseFloat(document.getElementById('distance').value) : null
    };

    // تحقق أساسي من البيانات
    if (!data.sender_name || !data.receiver_name || !data.receiver_email || data.weight === 0) {
        document.getElementById('modalError').textContent = 'الرجاء ملء جميع الحقول المطلوبة (الاسم، العنوان، البريد، الوزن).';
        document.getElementById('modalError').classList.remove('d-none');
        document.getElementById('modalSuccess').classList.add('d-none');
        return;
    }

    try {
        const response = await axios.post('/api/shipments/create/', data);

        document.getElementById('modalSuccess').textContent =
            `تم إنشاء الشحنة بنجاح! رقم التتبع: ${response.data.tracking_number}`;
        document.getElementById('modalSuccess').classList.remove('d-none');
        document.getElementById('modalError').classList.add('d-none');
        document.getElementById('createShipmentForm').reset();

        // مسح الإحداثيات والماركرز من الخرائط الصغيرة
        document.getElementById('senderLat').value = '';
        document.getElementById('senderLng').value = '';
        document.getElementById('receiverLat').value = '';
        document.getElementById('receiverLng').value = '';
        if (senderMarker) { senderMap.removeLayer(senderMarker); senderMarker = null; }
        if (receiverMarker) { receiverMap.removeLayer(receiverMarker); receiverMarker = null; }

        // إخفاء الـ Modal بعد 3 ثواني
        setTimeout(() => {
            const modalInstance = bootstrap.Modal.getInstance(document.getElementById('createShipmentModal'));
            if (modalInstance) modalInstance.hide();
            document.getElementById('modalSuccess').classList.add('d-none');
            loadShipments();
        }, 3000);

    } catch (error) {
        console.error('Error:', error.response?.data);
        let errorMsg = JSON.stringify(error.response?.data || 'حدث خطأ في إنشاء الشحنة', null, 2);
        document.getElementById('modalError').innerHTML = `حدث خطأ: <pre>${errorMsg}</pre>`;
        document.getElementById('modalError').classList.remove('d-none');
        document.getElementById('modalSuccess').classList.add('d-none');
    }
}

async function openUpdateStatus(shipmentId) {
    document.getElementById('updateShipmentId').value = shipmentId;
    document.getElementById('statusModalError').classList.add('d-none');

    // إعادة تعيين الحقول قبل الفتح
    document.getElementById('currentLocation').value = '';
    document.getElementById('statusLat').value = '';
    document.getElementById('statusLng').value = '';
    document.getElementById('statusNotes').value = '';

    const modalElement = document.getElementById('updateStatusModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener('shown.bs.modal', async function () {
        // تهيئة الخريطة مع مركز افتراضي، ثم تحديثها ببيانات الشحنة
        initStatusMap();

        try {
            // جلب تفاصيل الشحنة (يتطلب أن يكون المسار /api/shipments/ID/ مُعرّفاً في urls.py)
            const response = await axios.get(`/api/shipments/${shipmentId}/`);
            const shipment = response.data;

            document.getElementById('newStatus').value = shipment.status;

            let initialLat = DEFAULT_CENTER[0];
            let initialLng = DEFAULT_CENTER[1];

            if (statusMarker) { statusMap.removeLayer(statusMarker); statusMarker = null; }

            // إذا كان هناك موقع حالي في البيانات، استخدمه
            if (shipment.current_lat && shipment.current_lng) {
                initialLat = parseFloat(shipment.current_lat);
                initialLng = parseFloat(shipment.current_lng);
                document.getElementById('currentLocation').value = shipment.current_location_text || '';
                updateStatusMarker(initialLat, initialLng);
            } else if (shipment.sender_lat && shipment.sender_lng) {
                // وإلا، استخدم موقع المرسل كنقطة بداية للخريطة
                initialLat = parseFloat(shipment.sender_lat);
                initialLng = parseFloat(shipment.sender_lng);
            }

            // تحديث مركز الخريطة وحجمها
            statusMap.setView([initialLat, initialLng], 12);
            statusMap.invalidateSize();

        } catch (error) {
            // هذا هو مكان ظهور رسالة "حدث خطأ في جلب بيانات الشحنة."
            document.getElementById('statusModalError').textContent = 'حدث خطأ في جلب بيانات الشحنة.';
            document.getElementById('statusModalError').classList.remove('d-none');
        }
    }, { once: true });
}

async function submitStatusUpdate() {
    const shipmentId = document.getElementById('updateShipmentId').value;
    const newStatus = document.getElementById('newStatus').value;
    const currentLocation = document.getElementById('currentLocation').value;
    const statusLat = document.getElementById('statusLat').value;
    const statusLng = document.getElementById('statusLng').value;
    const statusNotes = document.getElementById('statusNotes').value; // جلب الملاحظات

    if (!newStatus) return;

    const data = {
        // يتم إرسال المفاتيح التي يتوقعها الـ Backend في views.py
        status: newStatus,
        location: currentLocation,
        latitude: statusLat || null,
        longitude: statusLng || null,
        notes: statusNotes || null // إرسال الملاحظات
    };

    // ** تحقق من أن جميع الحقول المطلوبة لـ Django موجودة **
    if (!data.location) {
        document.getElementById('statusModalError').textContent = 'الرجاء إدخال الموقع الحالي (نص).';
        document.getElementById('statusModalError').classList.remove('d-none');
        return;
    }


    try {
        // 🔥🔥🔥 تم تصحيح المسار ليتطابق مع urls.py
        const response = await axios.post(`/api/shipments/${shipmentId}/update-status/`, data);

        // إغلاق الـ Modal وإعادة تحميل القائمة
        const modalInstance = bootstrap.Modal.getInstance(document.getElementById('updateStatusModal'));
        if (modalInstance) modalInstance.hide();
        loadShipments();

    } catch (error) {
        console.error('Error updating status:', error.response?.data);
        let errorMsg = error.response?.data?.error || JSON.stringify(error.response?.data || 'حدث خطأ غير معروف.', null, 2);

        document.getElementById('statusModalError').innerHTML = `حدث خطأ: ${errorMsg}`;
        document.getElementById('statusModalError').classList.remove('d-none');
    }
}

// =======================================================
// 🚀 Initial Load
// =======================================================
document.addEventListener('DOMContentLoaded', () => {
    loadShipments();

    // تهيئة الخرائط الصغيرة عند فتح الـ Modal لأول مرة
    const createShipmentModalElement = document.getElementById('createShipmentModal');
    createShipmentModalElement.addEventListener('shown.bs.modal', function () {
        initSenderMap();
        initReceiverMap();
    }, { once: true });
});
