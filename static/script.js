setInterval(() => {
    fetch('/get_tasks')
    .then(response => response.json())
    .then(tasks => {
        tasks.forEach(task => {
            let now = new Date();
            let taskTime = task.time;
            let formattedTime = now.getHours().toString().padStart(2, '0') + ":" +
                                now.getMinutes().toString().padStart(2, '0');

            if (formattedTime === taskTime) {
                alert("Task Reminder: " + task.task);
                fetch(`/delete_task/${task.id}`, { method: 'POST' });
            }
        });
    });
}, 10000);
