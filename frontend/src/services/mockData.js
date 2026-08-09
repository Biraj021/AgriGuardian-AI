export const dashboardMockData = {
  farmName: "Pune South Farm",
  farmSize: "12.5 Acres",
  location: "Pune, Maharashtra",
  dateString: "Friday, 8 Aug 2026",
  timeString: "10:30 AM",
  farmerName: "Ramesh Patil",
  farmerRole: "Farmer",
  heroRecommendation: {
    decision: "Irrigate Today",
    confidence: 0.92,
    recommendedTime: "06:00 PM",
    estWater: "12,000 Liters",
    reasoning: [
      "Soil moisture is low (28%) which may stress the crop.",
      "No rainfall expected in the next 48 hours.",
      "Current temperature and humidity will increase crop water demand.",
      "Water level in storage is sufficient (85%)."
    ],
    timestamp: "2026-08-08T10:30:00Z"
  },
  liveStatus: {
    soilMoisture: { value: 28, unit: "%", status: "Low", range: "25% - 60%", color: "text-red-500 bg-red-50 border-red-100", sparkline: [35, 33, 30, 28, 29, 27, 28] },
    temperature: { value: 32, unit: "°C", status: "High", range: "18°C - 30°C", color: "text-red-500 bg-red-50 border-red-100", sparkline: [26, 28, 29, 31, 30, 32, 32] },
    humidity: { value: 45, unit: "%", status: "Normal", range: "40% - 70%", color: "text-green-500 bg-green-50 border-green-100", sparkline: [50, 48, 47, 45, 46, 44, 45] },
    rainfall: { value: 0, unit: "mm", status: "No Rain", range: "Next 24h", color: "text-amber-500 bg-amber-50 border-amber-100", sparkline: [0, 0, 0, 0, 0, 0, 0] },
    waterLevel: { value: 85, unit: "%", status: "Good", range: "30% - 100%", color: "text-green-500 bg-green-50 border-green-100", sparkline: [90, 88, 87, 86, 85, 84, 85] }
  },
  environmentalIntel: {
    weather: {
      currentTemp: 32,
      condition: "Sunny",
      feelsLike: 34,
      humidity: 42,
      wind: 12,
      forecast: [
        { day: "Today", temp: "32° / 20°", condition: "Sunny" },
        { day: "Sat", temp: "31° / 19°", condition: "Cloudy" },
        { day: "Sun", temp: "28° / 18°", condition: "Rain" },
        { day: "Mon", temp: "27° / 18°", condition: "Rain" },
        { day: "Tue", temp: "30° / 19°", condition: "Sunny" }
      ]
    },
    alerts: [
      { type: "Heatwave Alert", description: "High temperature conditions expected in your area.", dateRange: "08 Aug - 10 Aug 2026", status: "High Risk", severity: "danger" },
      { type: "No Flood Risk", description: "No flood risk in next 5 days.", dateRange: "Safe", status: "Safe", severity: "safe" },
      { type: "No Cyclone Risk", description: "No cyclone activity detected.", dateRange: "Safe", status: "Safe", severity: "safe" }
    ]
  },
  marketIntel: [
    { crop: "Wheat", currentPrice: "₹2,200", unit: "Quintal", change: "+2.4%", trend: "up", sparkline: [2100, 2120, 2180, 2150, 2190, 2200, 2200] },
    { crop: "Rice", currentPrice: "₹2,800", unit: "Quintal", change: "-1.2%", trend: "down", sparkline: [2850, 2830, 2810, 2840, 2820, 2790, 2800] }
  ],
  governmentSupport: [
    { title: "PM-KISAN Samman Nidhi", description: "Income support of ₹6,000 per year for all farmer families.", details: "Eligible • Next Installment: Aug 2026", status: "Eligible" },
    { title: "Kisan Credit Card (KCC)", description: "Low interest loan for farmers for agriculture needs.", details: "Eligible • Interest Rate: 4%", status: "Eligible" }
  ],
  analytics: {
    labels: ['02 Aug', '03 Aug', '04 Aug', '05 Aug', '06 Aug', '07 Aug', '08 Aug'],
    soilMoisture: [45, 42, 38, 35, 32, 29, 28],
    temperature: [26, 28, 29, 31, 30, 32, 32]
  },
  history: [
    { date: "08 Aug 2026", decision: "Irrigate Today", confidence: "92%", reason: "Low Soil Moisture (28%)" },
    { date: "05 Aug 2026", decision: "Do Not Irrigate", confidence: "88%", reason: "Expected Rainfall (12mm)" },
    { date: "02 Aug 2026", decision: "Irrigate", confidence: "95%", reason: "Critical Soil Dryness (<30%)" },
    { date: "30 Jul 2026", decision: "Irrigate", confidence: "90%", reason: "High Temperature (34°C)" },
    { date: "28 Jul 2026", decision: "Do Not Irrigate", confidence: "85%", reason: "High Humidity (75%)" }
  ]
};
