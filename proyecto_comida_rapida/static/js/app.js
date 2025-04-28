/**
 * Script principal para la aplicación de consultas IA
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const queryForm = document.getElementById('queryForm');
    const questionInput = document.getElementById('questionInput');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorContainer = document.getElementById('errorContainer');
    const sqlContainer = document.getElementById('sqlContainer');
    const sqlQuery = document.getElementById('sqlQuery');
    const chartContainer = document.getElementById('chartContainer');
    const tableContainer = document.getElementById('tableContainer');
    const tableHeader = document.getElementById('tableHeader');
    const tableBody = document.getElementById('tableBody');
    
    // Variable para almacenar la instancia del gráfico
    let resultsChart = null;
    
    // Event listener para el formulario
    queryForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Validación básica
        if (!questionInput.value.trim()) {
            questionInput.classList.add('is-invalid');
            return;
        }
        
        // Ocultar mensajes de error anteriores
        errorContainer.classList.add('d-none');
        errorContainer.textContent = '';
        questionInput.classList.remove('is-invalid');
        
        // Mostrar indicador de carga
        loadingIndicator.classList.remove('d-none');
        submitBtn.disabled = true;
        
        // Ocultar resultados anteriores
        sqlContainer.classList.add('d-none');
        chartContainer.classList.add('d-none');
        tableContainer.classList.add('d-none');
        
        try {
            // Preparar datos para enviar al servidor
            const formData = {
                question: questionInput.value.trim()
            };
            
            // Enviar petición al servidor
            const response = await fetch('/consulta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            // Comprobar si la respuesta fue exitosa
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error en la solicitud');
            }
            
            // Procesar la respuesta
            const data = await response.json();
            console.log("Datos recibidos del servidor:", data); // Log para depuración
            
            // Mostrar la consulta SQL generada
            sqlQuery.textContent = data.sql_query;
            sqlContainer.classList.remove('d-none');
            
            // Verificar si hay un error en los resultados
            if (data.results && data.results.error) {
                errorContainer.textContent = data.results.error;
                errorContainer.classList.remove('d-none');
                return;
            }
            
            // Verificar si tenemos resultados válidos para graficar
            if (data.results && data.results.labels && data.results.values) {
                // Renderizar el gráfico con los resultados
                renderChart(data.results);
            } 
            // Verificar si tenemos resultados tabulares
            else if (data.results && data.results.columns && data.results.rows) {
                // Si hay exactamente 2 columnas y la segunda es numérica, podemos intentar graficar también
                const columns = data.results.columns;
                const rows = data.results.rows;
                
                if (columns.length === 2 && rows.length > 0 && typeof rows[0][columns[1]] === 'number') {
                    // Extraer datos para gráfico
                    const graphData = {
                        labels: rows.map(row => String(row[columns[0]])),
                        values: rows.map(row => Number(row[columns[1]]))
                    };
                    renderChart(graphData);
                } else {
                    // Renderizar tabla con los resultados
                    renderTable(data.results);
                }
            }
            else {
                // Mostrar mensaje de error si no hay resultados válidos
                errorContainer.textContent = "No se pudieron obtener resultados válidos para mostrar.";
                errorContainer.classList.remove('d-none');
            }
            
        } catch (error) {
            // Mostrar mensaje de error
            console.error('Error:', error);
            errorContainer.textContent = `Error: ${error.message}`;
            errorContainer.classList.remove('d-none');
        } finally {
            // Ocultar indicador de carga
            loadingIndicator.classList.add('d-none');
            submitBtn.disabled = false;
        }
    });

    /**
     * Renderiza un gráfico con los datos proporcionados
     * @param {Object} data - Datos para el gráfico (labels y values)
     */
    function renderChart(data) {
        try {
            console.log("Renderizando gráfico con datos:", data); // Log para depuración
            
            // Validar que tenemos datos válidos
            if (!data || !Array.isArray(data.labels) || !Array.isArray(data.values) || 
                data.labels.length === 0 || data.values.length === 0) {
                throw new Error("Formato de datos inválido para el gráfico");
            }
            
            // Verificar que las longitudes de labels y values coinciden
            if (data.labels.length !== data.values.length) {
                console.warn("Advertencia: Las longitudes de labels y values no coinciden");
            }
            
            // Destruir gráfico existente si hay uno
            if (resultsChart) {
                resultsChart.destroy();
            }
            
            // Obtener el contexto del canvas
            const ctx = document.getElementById('resultsChart').getContext('2d');
            
            // Determinar colores dinámicamente según la cantidad de datos
            const backgroundColors = [];
            const borderColors = [];
            
            const colorPalette = [
                ['rgba(54, 162, 235, 0.7)', 'rgba(54, 162, 235, 1)'],   // Azul
                ['rgba(255, 99, 132, 0.7)', 'rgba(255, 99, 132, 1)'],   // Rojo
                ['rgba(255, 206, 86, 0.7)', 'rgba(255, 206, 86, 1)'],   // Amarillo
                ['rgba(75, 192, 192, 0.7)', 'rgba(75, 192, 192, 1)'],   // Verde
                ['rgba(153, 102, 255, 0.7)', 'rgba(153, 102, 255, 1)'], // Púrpura
                ['rgba(255, 159, 64, 0.7)', 'rgba(255, 159, 64, 1)'],   // Naranja
                ['rgba(199, 199, 199, 0.7)', 'rgba(199, 199, 199, 1)']  // Gris
            ];
            
            // Asignar colores para cada dato
            for (let i = 0; i < data.labels.length; i++) {
                const colorIndex = i % colorPalette.length;
                backgroundColors.push(colorPalette[colorIndex][0]);
                borderColors.push(colorPalette[colorIndex][1]);
            }
            
            // Determinar automáticamente si usar un gráfico de barras o de pastel
            let chartType = 'bar';
            if (data.labels.length <= 5) {
                // Usar gráfico de pastel para pocos datos
                chartType = 'pie';
            }
            
            // Crear configuración del gráfico
            const chartConfig = {
                type: chartType,
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Resultados',
                        data: data.values,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: chartType === 'pie', // Mostrar leyenda solo para gráficos de pastel
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (chartType === 'pie') {
                                        const value = context.parsed;
                                        const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${context.label}: ${value} (${percentage}%)`;
                                    } else {
                                        return `${context.label}: ${context.parsed.y}`;
                                    }
                                }
                            }
                        }
                    },
                    scales: chartType === 'bar' ? {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    } : {} // No mostrar escalas para gráficos de pastel
                }
            };
            
            // Crear nueva instancia del gráfico
            resultsChart = new Chart(ctx, chartConfig);
            
            // Mostrar el contenedor del gráfico
            chartContainer.classList.remove('d-none');
            
        } catch (error) {
            console.error("Error al renderizar el gráfico:", error);
            // Mostrar mensaje de error
            errorContainer.textContent = `Error al mostrar el gráfico: ${error.message}`;
            errorContainer.classList.remove('d-none');
        }
    }

    /**
     * Renderiza una tabla con los datos proporcionados
     * @param {Object} data - Datos para la tabla (columns y rows)
     */
    function renderTable(data) {
        try {
            console.log("Renderizando tabla con datos:", data); // Log para depuración
            
            // Validar que tenemos datos válidos
            if (!data || !Array.isArray(data.columns) || !Array.isArray(data.rows) || 
                data.columns.length === 0) {
                throw new Error("Formato de datos inválido para la tabla");
            }
            
            // Limpiar tabla anterior
            tableHeader.innerHTML = '';
            tableBody.innerHTML = '';
            
            // Crear encabezado de la tabla
            const headerRow = document.createElement('tr');
            data.columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column;
                th.scope = 'col';
                headerRow.appendChild(th);
            });
            tableHeader.appendChild(headerRow);
            
            // Crear filas de datos
            data.rows.forEach(row => {
                const tr = document.createElement('tr');
                
                // Si es un objeto con propiedades correspondientes a las columnas
                if (typeof row === 'object' && row !== null && !Array.isArray(row)) {
                    data.columns.forEach(column => {
                        const td = document.createElement('td');
                        td.textContent = row[column] !== undefined ? row[column] : '';
                        tr.appendChild(td);
                    });
                } 
                // Si es un array en el mismo orden que las columnas
                else if (Array.isArray(row)) {
                    row.forEach(cell => {
                        const td = document.createElement('td');
                        td.textContent = cell !== null ? cell : '';
                        tr.appendChild(td);
                    });
                }
                
                tableBody.appendChild(tr);
            });
            
            // Mostrar el contenedor de la tabla
            tableContainer.classList.remove('d-none');
            
        } catch (error) {
            console.error("Error al renderizar la tabla:", error);
            // Mostrar mensaje de error
            errorContainer.textContent = `Error al mostrar la tabla: ${error.message}`;
            errorContainer.classList.remove('d-none');
        }
    }
}); 