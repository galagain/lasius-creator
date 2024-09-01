const whitePart1 = "Your ";
const greenPart = "State-of-the-Art";
const whitePart2 = " Creation Tool (Creator)";

const whiteSpan1 = document.querySelector(".typed-text .white:first-child");
const greenSpan = document.querySelector(".typed-text .green");
const whiteSpan2 = document.querySelector(".typed-text .white:last-child");

const cursorSpan = document.querySelector(".cursor");

const typingDelay = 100;
const erasingDelay = 20;
const newTextDelay = 2000; // Delay between current and next text
let partIndex = 0;
let charIndex = 0;

function type() {
    if (partIndex === 0 && charIndex < whitePart1.length) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        whiteSpan1.textContent += whitePart1.charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else if (partIndex === 1 && charIndex < greenPart.length) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        greenSpan.textContent += greenPart.charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else if (partIndex === 2 && charIndex < whitePart2.length) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        whiteSpan2.textContent += whitePart2.charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else {
        cursorSpan.classList.remove("typing");
        if (partIndex < 2) {
            partIndex++;
            charIndex = 0;
            setTimeout(type, typingDelay);
        } else {
            setTimeout(erase, newTextDelay);
        }
    }
}

function erase() {
    if (partIndex === 2 && charIndex > 0) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        whiteSpan2.textContent = whitePart2.substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else if (partIndex === 1 && charIndex > 0) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        greenSpan.textContent = greenPart.substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else if (partIndex === 0 && charIndex > 0) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        whiteSpan1.textContent = whitePart1.substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else {
        cursorSpan.classList.remove("typing");
        if (partIndex > 0) {
            partIndex--;
            charIndex = (partIndex === 0) ? whitePart1.length : greenPart.length;
            setTimeout(erase, typingDelay);
        } else {
            setTimeout(type, newTextDelay);
        }
    }
}

document.addEventListener("DOMContentLoaded", function() {
    setTimeout(type, newTextDelay + 250);
});

