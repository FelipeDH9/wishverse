//Back To Top Button
function backTop(){
    const buttonTop = document.querySelector('.back-to-top');
    if (window.scrollY >= 350) {
      buttonTop.classList.add('show')
    }
    else {
      buttonTop.classList.remove('show')
    }
  };
  
window.addEventListener('scroll', function() {
    backTop()
});