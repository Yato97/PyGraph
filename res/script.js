const diapo = document.querySelector('.diapo')
let timer, elements, slides, slideWidth
elements = document.querySelector('.elements')
slides = Array.from(elements.children)
let next = document.querySelector('#nav-droite')
let prev = document.querySelector('#nav-gauche')
let compteur = 0
slideWidth = diapo.getBoundingClientRect().width
next.addEventListener('click', slideNext)
prev.addEventListener('click', slidePrev)
function slideNext(){
compteur++
if(compteur == slides.length){
    compteur = 0
}
let decal = -slideWidth * compteur
elements.style.transform = `translateX(${decal}px)`
}
function slidePrev(){
    compteur--
    if(compteur < 0){
        compteur = slides.length - 1
    }
    let decal = -slideWidth * compteur
    elements.style.transform = `translateX(${decal}px)`
}
window.addEventListener("resize", () => {
    slideWidth = diapo.getBoundingClientRect().width
    slideNext()
})
