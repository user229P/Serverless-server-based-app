document.addEventListener("DOMContentLoaded", function() {

    config= {
     
            "host": "http://13.234.135.57"
    }
    const host = config.host; // Set default host URL
    const loginURL = `${host}/login`; // Adjust endpoint based on your backend
    const logoutURL = `${host}/logout`; // Adjust endpoint based on your backend
    const registerURL = `${host}/signup`; // Adjust endpoint based on your backend
    // const registerURL = `https://k3g2dgdr7nawlvpn7tjmaxkhre0foznr.lambda-url.ap-southeast-2.on.aws/`
    const addTaskURL = `${host}/add_task`; // Adjust endpoint based on your backend
    const viewTasksURL = `${host}/view_task`; // Adjust endpoint based on your backend
    const processImageURL = `${host}/process_image`; // Add the endpoint for image processing

    console.log(host);

    // Check if user is logged in
    const token = sessionStorage.getItem('token');
    if (token) {
        sessionStorage.setItem('isLoggedIn', true);
    }
    

    // Check session storage for user login status
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    if (isLoggedIn) {
        if(document.getElementById('loginButton') != null) {
            document.getElementById('loginButton').style.display = 'none';
        }
        if (document.getElementById('registerButton') != null) {
            document.getElementById('registerButton').style.display = 'none';
        }
    } else {
        
        if (document.getElementById('addTaskButton') != null) {
            document.getElementById('addTaskButton').style.display = 'none';
        }

        if (document.getElementById('logoutButton') != null) {
            document.getElementById('logoutButton').style.display = 'none';
        }

        if (document.getElementById('viewTasksButton') != null) {
            document.getElementById('viewTasksButton').style.display = 'none';
        }

        if (document.getElementById('process_image') != null) {
            document.getElementById('process_image').style.display = 'none';
        }
  
    }

    // Event listeners for buttons
    document.getElementById('loginButton')?.addEventListener('click', function() {
        window.location.href = 'login.html';
    });

    document.getElementById('registerButton')?.addEventListener('click', function() {
        window.location.href = 'register.html';
    });

    document.getElementById('addTaskButton')?.addEventListener('click', function() {
        window.location.href = 'add_task.html';
    });

    document.getElementById('viewTasksButton')?.addEventListener('click', function() {
        window.location.href = 'task.html';
    });


    if (isLoggedIn) {
        const token = sessionStorage.getItem('token')
        axios.post(viewTasksURL,{token: token})
        .then(response => {
            if (response.status == 200) {
                console.log(response.data);
                const tasks = response.data.tasks; // Adjust based on your API response structure
                const tasksList = document.getElementById('tasksList');

                console.log(response.data.tasks);
                
                if (response.data.length === 0) { 
                    tasksList.innerHTML = '<p class="text-center">No tasks available.</p>';
                }
                else {
                    let html = '<ul class="list-group">';
                    tasks.forEach(task => {
                        html += `
                            <li class="list-group-item">
                                <h5>${task.title}</h5>
                                <p>${task.description}</p>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    tasksList.innerHTML = html;
                }
            } else {
                alert('Failed to fetch tasks: ' + response.data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
            alert('An error occurred while fetching tasks. Please try again.');
        });
    }
});
