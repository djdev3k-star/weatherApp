document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("weather-form");
    const dashboard = document.getElementById("weather-dashboard");
    const errorDiv = document.getElementById("error-message");
    const forecastTypeToggle = document.getElementById("forecast-type");
    const themeToggle = document.getElementById("theme-toggle");

    // --- Weather code to Font Awesome icon mapping ---
    const weatherIcons = {
        0:  { icon: "fa-sun", desc: "Clear sky" },
        1:  { icon: "fa-cloud-sun", desc: "Mainly clear" },
        2:  { icon: "fa-cloud-sun", desc: "Partly cloudy" },
        3:  { icon: "fa-cloud", desc: "Overcast" },
        45: { icon: "fa-smog", desc: "Fog" },
        48: { icon: "fa-smog", desc: "Depositing rime fog" },
        51: { icon: "fa-cloud-rain", desc: "Light drizzle" },
        53: { icon: "fa-cloud-rain", desc: "Moderate drizzle" },
        55: { icon: "fa-cloud-showers-heavy", desc: "Dense drizzle" },
        56: { icon: "fa-cloud-meatball", desc: "Light freezing drizzle" },
        57: { icon: "fa-cloud-meatball", desc: "Dense freezing drizzle" },
        61: { icon: "fa-cloud-showers-heavy", desc: "Slight rain" },
        63: { icon: "fa-cloud-showers-heavy", desc: "Moderate rain" },
        65: { icon: "fa-cloud-showers-heavy", desc: "Heavy rain" },
        66: { icon: "fa-cloud-meatball", desc: "Light freezing rain" },
        67: { icon: "fa-cloud-meatball", desc: "Heavy freezing rain" },
        71: { icon: "fa-snowflake", desc: "Slight snow fall" },
        73: { icon: "fa-snowflake", desc: "Moderate snow fall" },
        75: { icon: "fa-snowflake", desc: "Heavy snow fall" },
        77: { icon: "fa-snowflake", desc: "Snow grains" },
        80: { icon: "fa-cloud-showers-heavy", desc: "Slight rain showers" },
        81: { icon: "fa-cloud-showers-heavy", desc: "Moderate rain showers" },
        82: { icon: "fa-cloud-showers-heavy", desc: "Violent rain showers" },
        85: { icon: "fa-snowflake", desc: "Slight snow showers" },
        86: { icon: "fa-snowflake", desc: "Heavy snow showers" },
        95: { icon: "fa-bolt", desc: "Thunderstorm" },
        96: { icon: "fa-bolt", desc: "Thunderstorm with slight hail" },
        99: { icon: "fa-bolt", desc: "Thunderstorm with heavy hail" }
    };

    // --- Helper: Human-friendly date/time ---
    function formatDateTime(dtString) {
        const d = new Date(dtString);
        return d.toLocaleString(undefined, {
            weekday: "short",
          //  year: "numeric",
            month: "short",
            day: "numeric",
        //    hour: "2-digit",
        //    minute: "2-digit"
        });
    }

    // --- Main Dashboard Rendering Function ---
    function renderDashboard(data) {
        const { location, units, forecast_type, weather } = data;
        let html = `<h2>${location}</h2>`;

        // --- Current Weather ---
        if (weather.current) {
            const code = weather.current.weather_code;
            const icon = weatherIcons[code] ? weatherIcons[code].icon : "";
            const desc = weatherIcons[code] ? weatherIcons[code].desc : "Unknown";
            html += `
                <div class="row mb-3 align-items-center">
                    <div class="col-auto">
                        ${icon ? `<i class="fas ${icon} fa-3x text-primary" title="${desc}" aria-label="${desc}"></i>` : ""}
                    </div>
                    <div class="col">
                        <strong>${desc}</strong><br>
                        Temp: ${weather.current.temperature_2m}°${units === "celsius" ? "C" : "F"}
                        &nbsp;| Feels like: ${weather.current.apparent_temperature}°${units === "celsius" ? "C" : "F"}
                        <br>
                        Wind: ${weather.current.wind_speed_10m} ${units === "celsius" ? "km/h" : "mph"} (${weather.current.wind_direction_10m}°)
                        <br>
                        Humidity: ${weather.current.relative_humidity_2m}% | UV: ${weather.current.uv_index}
                    </div>
                </div>
            `;
        }

        // --- Forecast Table ---
        let forecast = weather[forecast_type];
        if (forecast && forecast.time) {
            html += `<div class="table-responsive"><table class="table table-striped"><thead><tr>`;
            html += `<th>Date/Time</th><th>Weather</th>`;
            if (forecast.temperature_2m) html += `<th>Temp (${units === "celsius" ? "°C" : "°F"})</th>`;
            if (forecast.apparent_temperature) html += `<th>Feels Like</th>`;
            if (forecast.temperature_2m_max) html += `<th>Max Temp</th>`;
            if (forecast.temperature_2m_min) html += `<th>Min Temp</th>`;
            if (forecast.wind_speed_10m) html += `<th>Wind</th>`;
           // if (forecast.wind_speed_10m_max) html += `<th>Max Wind</th>`;
            if (forecast.wind_direction_10m) html += `<th>Wind Dir</th>`;
          //  if (forecast.wind_direction_10m_dominant) html += `<th>Dom Wind Dir</th>`;
            if (forecast.precipitation) html += `<th>Precipitation</th>`;
           // if (forecast.precipitation_sum) html += `<th>Precip Sum</th>`;
            if (forecast.precipitation_probability) html += `<th>Precip Prob</th>`;
          //  if (forecast.precipitation_probability_max) html += `<th>Max Precip Prob</th>`;
            if (forecast.relative_humidity_2m) html += `<th>Humidity</th>`;
         //   if (forecast.relative_humidity_2m_max) html += `<th>Max Humidity</th>`;
            if (forecast.uv_index) html += `<th>UV Index</th>`;
        //    if (forecast.uv_index_max) html += `<th>Max UV</th>`;
            html += `</tr></thead><tbody>`;

            for (let i = 0; i < forecast.time.length; i++) {
                html += `<tr>`;
                // Date/Time
                html += `<td>${formatDateTime(forecast.time[i])}</td>`;
                // Icon
                let code = null;
                if (forecast.weather_code) code = forecast.weather_code[i];
                const icon = code && weatherIcons[code] ? weatherIcons[code].icon : "";
                const desc = code && weatherIcons[code] ? weatherIcons[code].desc : "";
                html += `<td>${icon ? `<i class="fas ${icon} fa-lg text-primary" title="${desc}" aria-label="${desc}"></i>` : ""}</td>`;
                // Forecast data columns
                if (forecast.temperature_2m) html += `<td>${forecast.temperature_2m[i]}</td>`;
                if (forecast.apparent_temperature) html += `<td>${forecast.apparent_temperature[i]}</td>`;
                if (forecast.temperature_2m_max) html += `<td>${forecast.temperature_2m_max[i]}</td>`;
                if (forecast.temperature_2m_min) html += `<td>${forecast.temperature_2m_min[i]}</td>`;
                if (forecast.wind_speed_10m) html += `<td>${forecast.wind_speed_10m[i]}</td>`;
            //    if (forecast.wind_speed_10m_max) html += `<td>${forecast.wind_speed_10m_max[i]}</td>`;
                if (forecast.wind_direction_10m) html += `<td>${forecast.wind_direction_10m[i]}</td>`;
            //    if (forecast.wind_direction_10m_dominant) html += `<td>${forecast.wind_direction_10m_dominant[i]}</td>`;
                if (forecast.precipitation) html += `<td>${forecast.precipitation[i]}</td>`;
            //    if (forecast.precipitation_sum) html += `<td>${forecast.precipitation_sum[i]}</td>`;
                if (forecast.precipitation_probability) html += `<td>${forecast.precipitation_probability[i] ?? "-"}</td>`;
            //    if (forecast.precipitation_probability_max) html += `<td>${forecast.precipitation_probability_max[i] ?? "-"}</td>`;
                if (forecast.relative_humidity_2m) html += `<td>${forecast.relative_humidity_2m[i]}</td>`;
            //    if (forecast.relative_humidity_2m_max) html += `<td>${forecast.relative_humidity_2m_max[i]}</td>`;
                if (forecast.uv_index) html += `<td>${forecast.uv_index[i]}</td>`;
            //    if (forecast.uv_index_max) html += `<td>${forecast.uv_index_max[i]}</td>`;
                html += `</tr>`;
            }
            html += `</tbody></table></div>`;
        }


            const container = document.getElementById("weather-dashboard-container");
            container.classList.remove("d-none");
            // Clear previous content and show dashboard
            dashboard.classList.remove("d-none");
            // Render the HTML
            dashboard.innerHTML = html;
        }

    // Load defaults from sessionStorage
    const defaultLocation = sessionStorage.getItem("defaultLocation");
    if (defaultLocation) {
        const { city, lat, lon, units, forecastType } = JSON.parse(defaultLocation);
        document.getElementById("city").value = city || "";
        document.getElementById("lat").value = lat || "";
        document.getElementById("lon").value = lon || "";
        document.getElementById("units").value = units || "celsius";
        forecastTypeToggle.checked = forecastType === "daily";
    }

    form.onsubmit = async function (e) {
        e.preventDefault();
        errorDiv.classList.add("d-none");
        dashboard.innerHTML = "";

        const city = document.getElementById("city").value.trim();
        const lat = document.getElementById("lat").value.trim();
        const lon = document.getElementById("lon").value.trim();
        const units = document.getElementById("units").value;
        const forecastType = forecastTypeToggle.checked ? "daily" : "hourly";

        // Save as default
        localStorage.setItem("defaultLocation", JSON.stringify({ city, lat, lon, units, forecastType }));

        try {
            const res = await fetch("/api/weather", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ city, lat, lon, units, forecast_type: forecastType })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Unknown error");

            renderDashboard(data);
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove("d-none");


        }
    };

    forecastTypeToggle.onchange = () => form.onsubmit(new Event("submit"));

    themeToggle.onclick = function () {
        const html = document.documentElement;
        const current = html.getAttribute("data-bs-theme");
        html.setAttribute("data-bs-theme", current === "light" ? "dark" : "light");
        localStorage.setItem("theme", html.getAttribute("data-bs-theme"));
    };

    // Optional: Load theme from localStorage
    const theme = localStorage.getItem("theme");
    if (theme) {
        document.documentElement.setAttribute("data-bs-theme", theme);
    }

    // Trigger initial load if defaults exist
    if (defaultLocation) {
        form.onsubmit(new Event("submit"));
    }
});
