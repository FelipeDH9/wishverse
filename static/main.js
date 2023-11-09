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


// dialog modal for delete confirmation
const open_buttons = document.querySelectorAll("button.delete-btn");
const modal = document.querySelector('dialog');
const modal_id = document.getElementById("modal_id");

const close = document.getElementById("close");

open_buttons.forEach((button)=>{
  button.addEventListener('click', ()=> {
    // get button value with button.value
    const product_id = button.value;
    // update the value of the input in dialog to product id
    modal_id.value = product_id;
    modal.showModal();
  })
});


close.onclick = function(){
  modal.close();
  modal_id.value = 0;
};