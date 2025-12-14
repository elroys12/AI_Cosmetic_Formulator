import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

const formatProperties = (props) => {
    if (!props) return "-";
    if (typeof props === 'string') return props;
    if (typeof props === 'object') {
        return Object.entries(props)
            .map(([key, val]) => `${key}: ${val === null || val === undefined ? '-' : val}`)
            .join(" | ");
    }
    return String(props);
};

const adaptResponse = (rawData) => {
    const core = rawData.output_data || rawData.data || {};
    const predictionData = {
        name: core.nama_senyawa || core.name || "Senyawa Tidak Dikenal",
        formula: core.formula || "-",
        smiles: core.smiles || "-",
        description: core.description || core.justifikasi || "Tidak ada deskripsi tersedia.",
        
        dosage: core.dosage || "N/A - Data Agent 3 Kosong",
        contraindications: core.contraindications || [],
        safetyNotes: core.safety_notes || "-",
        usageGuidelines: core.usage_guidelines || "N/A",
        
        properties: formatProperties(core.sifat_kimia || core.properties)
    };
    
    return {
        id: rawData.id || rawData.history_id, 
        historyId: rawData.history_id || rawData.id, 
        conversationId: rawData.conversation_id || null, 
        
        date: rawData.created_at ? new Date(rawData.created_at).toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' }) : null,
        time: rawData.created_at ? new Date(rawData.created_at).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) : null,
        
        recommendations: (core.recommendations || []).map(rec => ({
            name: rec.name || rec.nama_senyawa || "Varian Alternatif",
            formula: rec.formula || "-",
            smiles: rec.smiles || "-",
            justification: rec.justification || rec.description || "-",
            
            properties: formatProperties(rec.properties || rec.sifat_kimia),
            pros: rec.pros || [],
            cons: rec.cons || [],
            priceRange: rec.price_range || "N/A"
        })),

        prediction: predictionData,
    };
};

api.interceptors.request.use(config => {
    const token = localStorage.getItem("token"); 
    
    if (token) { 
        config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
}, error => {
    return Promise.reject(error);
});

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401 && 
            !error.config.url.includes("/auth/")) {
            
            console.error("Token Expired/Invalid. Force Logout.");
            localStorage.removeItem("token");
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    login: async (email, password) => {
        const response = await api.post("auth/login", { email, password });
        return response.data;
    },
    register: async (fullName, email, password) => {
        const response = await api.post("auth/register", { full_name: fullName, email, password });
        return response.data;
    }
};

export const dataAPI = {
    getRecommendation: async (payload) => {
        const response = await api.post("analyze", payload);

        const rawData = response.data; 

        if (!rawData.success) { 
            throw new Error(rawData.message || "API returned failure status.");
        }

        return adaptResponse(rawData);
    },
    getHistory: async () => {
        const response = await api.get("history");
        const rawHistoryList = Array.isArray(response.data) ? response.data : (response.data.data || []);
        
        return rawHistoryList.map(item => ({
            ...adaptResponse(item),
            title: (item.output_data?.nama_senyawa) || (item.output_data?.name) || "Analisis Tanpa Judul"
        }));
    },

    deleteHistory: async (id) => {
        const response = await api.delete(`history/${id}`);
        return response.data;
    }
};