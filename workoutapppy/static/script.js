document.addEventListener('DOMContentLoaded', function() {
    const muscleGroupColors = {
        chest: '#FF5733',
        back: '#33FF57',
        hamstrings: '#3357FF',
        quads: '#FF33A8',
        triceps: '#FFC300',
        biceps: '#33FFF9',
        shoulders: '#8E44AD'
    };

    let chartInstance = null;

    const days = document.querySelectorAll('.calendar .day');
    const tooltip = document.getElementById('tooltip');
    const tooltipContent = document.getElementById('tooltip-content');
    const tooltipChart = document.getElementById('tooltip-chart').getContext('2d');

    days.forEach(day => {
        day.addEventListener('mouseover', function(event) {
            const workouts = JSON.parse(this.dataset.workouts);
            if (workouts.length === 0) {
                tooltipContent.innerHTML = 'No workouts';
                tooltip.classList.add('small');
                if (chartInstance) {
                    chartInstance.destroy();
                    chartInstance = null;
                }
            } else {
                let content = '';
                const muscleGroupVolumes = {
                    chest: 0,
                    back: 0,
                    hamstrings: 0,
                    quads: 0,
                    triceps: 0,
                    biceps: 0,
                    shoulders: 0
                };

                workouts.forEach(workout => {
                    const volume = workout.weight * workout.reps;
                    content += `${workout.body_part} - ${workout.exercise}: ${workout.weight} lbs, ${workout.reps} reps<br>`;
                    if (muscleGroupVolumes[workout.body_part] !== undefined) {
                        muscleGroupVolumes[workout.body_part] += volume;
                    }
                });

                tooltipContent.innerHTML = content;
                tooltip.classList.remove('small');

                const chartData = {
                    labels: Object.keys(muscleGroupVolumes),
                    datasets: [{
                        label: 'Total Volume',
                        data: Object.values(muscleGroupVolumes),
                        backgroundColor: Object.keys(muscleGroupVolumes).map(group => muscleGroupColors[group])
                    }]
                };

                if (chartInstance) {
                    chartInstance.destroy();
                }

                chartInstance = new Chart(tooltipChart, {
                    type: 'bar',
                    data: chartData,
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }

            tooltip.style.display = 'block';
            tooltip.style.left = `${event.pageX + 10}px`;
            tooltip.style.top = `${event.pageY + 10}px`;
        });

        day.addEventListener('mouseout', function() {
            tooltip.style.display = 'none';
            if (chartInstance) {
                chartInstance.destroy();
                chartInstance = null;
            }
        });
    });

    const bodyPartSelector = document.getElementById('body-part');
    const exerciseSelector = document.getElementById('exercise');

    bodyPartSelector.addEventListener('change', function() {
        const selectedGroup = this.value;
        const options = exerciseSelector.querySelectorAll('option');

        // Reset the exercise selector
        exerciseSelector.value = '';
        options.forEach(option => {
            if (option.dataset.group === selectedGroup) {
                option.style.display = 'block'; // Show option
            } else {
                option.style.display = 'none'; // Hide option
            }
        });
    });

    // Event listeners for weight and reps sliders
    const weightSlider = document.getElementById('weight');
    const weightValue = document.getElementById('weight-value');
    const repsSlider = document.getElementById('reps');
    const repsValue = document.getElementById('reps-value');

    weightSlider.addEventListener('input', function() {
        weightValue.textContent = this.value;
    });

    repsSlider.addEventListener('input', function() {
        repsValue.textContent = this.value;
    });
});
