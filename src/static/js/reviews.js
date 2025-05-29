// reviews.js - без изменений
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function() {
    const btn = this.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Обработка...';
  });
});

document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const value = this.dataset.value;
            document.getElementById('rating-value').value = value;
            stars.forEach(s => {
                s.classList.remove('active');
                if(s.dataset.value <= value) {
                    s.classList.add('active');
                    s.innerHTML = '★';
                } else {
                    s.classList.remove('active');
                    s.innerHTML = '☆';
                }
            });
        });
    });
});

// Модальное окно для записи на курс
function handleEnrollment(courseName) {
    const modal = document.getElementById('enrollmentModal');
    const courseTitle = document.getElementById('courseTitle');
    const form = document.getElementById('enrollForm');
    courseTitle.textContent = courseName;
    form.action = `/enroll/${courseName}`;
    modal.style.display = 'block';
    
    // Закрытие модального окна
    document.querySelector('.close').onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}