document.addEventListener('DOMContentLoaded', () => {
    (function ($) {
        $('.image-input').on('change', function () {
            let url = ''

            if (this.files.length) {
                url = URL.createObjectURL(this.files[0])
            }

            $(this).parent().find('.image-preview')[0].src = url
            console.log(this.files, url, $(this).parent().find('.image-preview'))
        })
    })(django.jQuery);
})

