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

        document.getElementById('process_image')?.addEventListener('click', function() {
            window.location.href = 'image.html';
        });
 
        document.getElementById('logoutButton')?.addEventListener('click', function() {
            axios.post(logoutURL, { token: sessionStorage.getItem('token') })
            .then(response => {
                if (response.status == 200) {
                    console.log(response);
                    sessionStorage.removeItem('isLoggedIn');
                    sessionStorage.removeItem('token');
                    window.location.href = 'login.html';
                } else {
                    alert('Logout failed: ' + response.data.message);
                }
            })
            .catch(error => {
                console.error('Error during logout:', error);
                alert('An error occurred. Please try again.');
            });
        });

        // Handle login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevent form submission
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;

                axios.post(loginURL, { username, password })
                    .then(response => {
                        if (response.status == 200) {
                            sessionStorage.setItem('isLoggedIn', 'true');
                            sessionStorage.setItem('token', response.data.access_token);
                            window.location.href = 'index.html';
                        } else {
                            console.log(response);
                            alert('Login failed: ' + response.data);
                        }
                    })
                    .catch(error => {
                        console.error('Error during login:', error);
                        alert('An error occurred. Please try again.');
                    });
            });
        }
        

        // Handle registration form submission
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevent form submission

                const username = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                console.log(name, email, password);

                axios.post(registerURL, {
                    
                        username: username,
                        email: email,
                        password: password
                    
                     

                })
                    .then(response => {
                        if (response.status == 200) {
                            window.location.href = 'login.html';
                        } else {
                            alert('Registration failed: ' + response.data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error during registration:', error);
                        alert('An error occurred. Please try again.');
                    });
            });
        }



         // Handle image upload and processing
         const imageForm = document.getElementById('imageForm');
         if (imageForm) {
             imageForm.addEventListener('submit', function(e) {
                 e.preventDefault(); // Prevent form submission

                 const imageFile = document.getElementById('imageUpload').files[0];
                 const format = document.getElementById('formatSelect').value;
                 const rotateAngle = document.getElementById('rotateAngle').value;

                 const formData = new FormData();
                 formData.append('image', imageFile);
                 formData.append('format', format);
                 formData.append('rotate', rotateAngle);

                 axios.post(processImageURL, formData, {
                     headers: {
                         'Content-Type': 'multipart/form-data'
                     }
                 })
                 .then(response => {
                     if (response.status === 200) {
                         document.getElementById('result').classList.remove('d-none');
                         document.getElementById('imageLink').href = response.data.imageUrl;
                     } else {
                         alert('Failed to process image: ' + response.data.message);
                     }
                 })
                 .catch(error => {
                     console.error('Error during image processing:', error);
                     alert('An error occurred. Please try again.');
                 });
             });
         }

        

        // Handle task creation form submission
        const addTaskForm = document.getElementById('addTaskForm');
        if (addTaskForm) {
            addTaskForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevent form submission

                const taskTitle = document.getElementById('taskTitle').value;
                const taskDescription = document.getElementById('taskDescription').value;

                // Ensure user is logged in before allowing task creation
                if (isLoggedIn) {
                    axios.post(addTaskURL, { title: taskTitle, description: taskDescription, token: sessionStorage.getItem('token') })
                        .then(response => {
                            if (response.status == 200) {
                                window.location.href = 'index.html';
                            } else {
                                alert('Failed to add task: ' + response.data.message);
                            }
                        })
                        .catch(error => {
                            console.error('Error during task addition:', error);
                            alert('An error occurred. Please try again.');
                        });
                } else {
                    alert('You must be logged in to add a task.');
                }
            });
        }

});
