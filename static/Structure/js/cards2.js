const initSlider = () => {
  const imageList = document.querySelector(".slider-wrapper .image-list");
  const slideButtons = document.querySelectorAll(".slider-wrapper .slide-button");
  const sliderScrollbar = document.querySelector(".container .slider-scrollbar");
  const scrollbarThumb = sliderScrollbar.querySelector(".scrollbar-thumb");
  const maxScrollLeft = imageList.scrollWidth - imageList.clientWidth;

  // Handle touch events for swipe
  let touchStartX = 0;

  imageList.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
          touchStartX = e.touches[0].clientX;
      }
  });

  imageList.addEventListener("touchmove", (e) => {
      if (e.touches.length === 1) {
          const touchEndX = e.touches[0].clientX;
          const touchDelta = touchStartX - touchEndX;

          if (Math.abs(touchDelta) > 50) {
              const direction = touchDelta > 0 ? 1 : -1;
              const scrollAmount = imageList.clientWidth * direction;
              imageList.scrollBy({ left: scrollAmount, behavior: "smooth" });
          }
      }
  });

  // Handle touch events for scrollbar
  scrollbarThumb.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
          touchStartX = e.touches[0].clientX;
      }
  });

  scrollbarThumb.addEventListener("touchmove", (e) => {
      if (e.touches.length === 1) {
          const touchEndX = e.touches[0].clientX;
          const touchDelta = touchStartX - touchEndX;

          const thumbPosition = scrollbarThumb.offsetLeft;
          const maxThumbPosition = sliderScrollbar.clientWidth - scrollbarThumb.offsetWidth;

          const deltaX = touchEndX - touchStartX;
          const newThumbPosition = thumbPosition - deltaX;

          const boundedPosition = Math.max(0, Math.min(maxThumbPosition, newThumbPosition));
          const scrollPosition = (boundedPosition / maxThumbPosition) * maxScrollLeft;

          scrollbarThumb.style.left = `${boundedPosition}px`;
          imageList.scrollLeft = scrollPosition;

          // Update touch start position for the next move
          touchStartX = touchEndX;
      }
  });

  // Handle scrollbar thumb drag
  scrollbarThumb.addEventListener("mousedown", (e) => {
      const startX = e.clientX;
      const thumbPosition = scrollbarThumb.offsetLeft;
      const maxThumbPosition = sliderScrollbar.clientWidth - scrollbarThumb.offsetWidth;

      const handleMouseMove = (e) => {
          const deltaX = e.clientX - startX;
          const newThumbPosition = thumbPosition + deltaX;
          const boundedPosition = Math.max(0, Math.min(maxThumbPosition, newThumbPosition));
          const scrollPosition = (boundedPosition / maxThumbPosition) * maxScrollLeft;

          scrollbarThumb.style.left = `${boundedPosition}px`;
          imageList.scrollLeft = scrollPosition;
      };

      const handleMouseUp = () => {
          document.removeEventListener("mousemove", handleMouseMove);
          document.removeEventListener("mouseup", handleMouseUp);
      };

      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
  });

  // Slide images according to the slide button clicks
  slideButtons.forEach((button) => {
      button.addEventListener("click", () => {
          const direction = button.id === "prev-slide" ? -1 : 1;
          const scrollAmount = imageList.clientWidth * direction;
          imageList.scrollBy({ left: scrollAmount, behavior: "smooth" });
      });
  });

  // Show or hide slide buttons based on scroll position
  const handleSlideButtons = () => {
      slideButtons[0].style.display = imageList.scrollLeft <= 0 ? "none" : "flex";
      slideButtons[1].style.display = imageList.scrollLeft >= maxScrollLeft ? "none" : "flex";
  };

  // Update scrollbar thumb position based on image scroll
  const updateScrollThumbPosition = () => {
      const scrollPosition = imageList.scrollLeft;
      const thumbPosition = (scrollPosition / maxScrollLeft) * (sliderScrollbar.clientWidth - scrollbarThumb.offsetWidth);
      scrollbarThumb.style.left = `${thumbPosition}px`;
  };

  // Call these two functions when image list scrolls
  imageList.addEventListener("scroll", () => {
      updateScrollThumbPosition();
      handleSlideButtons();
  });

  window.addEventListener("resize", () => {
    let maxScrollLeft = imageList.scrollWidth - imageList.clientWidth;
      updateScrollThumbPosition();
      handleSlideButtons();
  });

  window.addEventListener("load", () => {
      updateScrollThumbPosition();
      handleSlideButtons();
  });
};

initSlider();
