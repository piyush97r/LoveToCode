var myCodeMirror = CodeMirror(document.querySelector('.editor'), {
	theme: 'slugbay',
	indentUnit: 2,
	tabSize: 4,
	readOnly: false,
	indentWithTabs: false,
	firstLineNumber: 1,
	lineNumbers: true,
	viewportMargin: Infinity,
	matchBrackets: true,
	autoCloseBrackets: true,
	foldGutter: true,
	gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
	styleActiveLine: true,
	dragDrop: true,
	//allowDropFileTypes: [],
	mode: 'python'
});
//For selector.....!
// set up select boxes
$('.selectholder').each(function () {
	$(this).children().hide();
	var description = $(this).children('label').text();
	$(this).append('<span class="desc">' + description + '</span>');
	$(this).append('<span class="pulldown"></span>');
	// set up dropdown element
	$(this).append('<div class="selectdropdown"></div>');
	$(this).children('select').children('option').each(function () {
		if ($(this).attr('value') != '0') {
			$drop = $(this).parent().siblings('.selectdropdown');
			var name = $(this).attr('value');
			$drop.append('<span>' + name + '</span>');
		}
	});
	// on click, show dropdown
	$(this).click(function () {
		if ($(this).hasClass('activeselectholder')) {
			// roll up roll up
			$(this).children('.selectdropdown').slideUp(200);
			$(this).removeClass('activeselectholder');
			// change span back to selected option text
			if ($(this).children('select').val() != '0') {
				$(this).children('.desc').fadeOut(100, function () {
					$(this).text($(this).siblings("select").val());
					$(this).fadeIn(100);
				});
			}
		}
		else {
			// if there are any other open dropdowns, close 'em
			$('.activeselectholder').each(function () {
				$(this).children('.selectdropdown').slideUp(200);
				// change span back to selected option text
				if ($(this).children('select').val() != '0') {
					$(this).children('.desc').fadeOut(100, function () {
						$(this).text($(this).siblings("select").val());
						$(this).fadeIn(100);
					});
				}
				$(this).removeClass('activeselectholder');
			});
			// roll down
			$(this).children('.selectdropdown').slideDown(200);
			$(this).addClass('activeselectholder');
			// change span to show select box title while open
			if ($(this).children('select').val() != '0') {
				$(this).children('.desc').fadeOut(100, function () {
					$(this).text($(this).siblings("select").children("option[value=0]").text());
					$(this).fadeIn(100);
				});
			}
		}
	});
});
// select dropdown click action
$('.selectholder .selectdropdown span').click(function () {
	$(this).siblings().removeClass('active');
	$(this).addClass('active');
	var value = $(this).text();
	$(this).parent().siblings('select').val(value);
	$(this).parent().siblings('.desc').fadeOut(100, function () {
		$(this).text(value);
		$(this).fadeIn(100);
	});
});
