tinymce.init({ 
		selector:'#tinymce1',
		language: 'zh_CN',
		plugins: ['lists',
				  'advlist',
				  'fullscreen',
				  'fullpage',
				  'code',
				  'autosave',
				  'anchor',
				  'textcolor colorpicker',
				  'emoticons',
				  'image'
		],
		menubar: ['view', 'insert'],
		toolbar1: 'insertfile undo redo | styleselect | forecolor backcolor bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | print preview media fullpage | fullpage_default_title: "TinyMCE - Configuration:fullpage_default_title" | fullscreen',
		toolbar2: 'fontselect fontsizeselect | emoticons | code restoredraft ',
		advlist_bullet_styles: 'square',
        advlist_number_styles: 'lower-alpha,lower-roman,upper-alpha,upper-roman',
        content_css : '/mycontent.css',
        fontsize_formats: '8pt 10pt 12pt 14pt 18pt 24pt 36pt',
        image_caption: 'true',
  		file_browser_callback_types: 'file image media',
		images_upload_handler: function (blobInfo, success, failure) {
		    var xhr, formData;

		    xhr = new XMLHttpRequest();
		    xhr.withCredentials = false;
		    xhr.open('POST', '/upload');

		    xhr.onload = function() {
		      var json;

		      if (xhr.status != 200) {
		        failure('HTTP Error: ' + xhr.status);
		        return;
		      }

		      json = JSON.parse(xhr.responseText);

		      if (!json || typeof json.location != 'string') {
		        failure('Invalid JSON: ' + xhr.responseText);
		        return;
		      }

		      success(json.location);
		    };

		    formData = new FormData();
		    formData.append('file', blobInfo.blob(), blobInfo.filename());
		    xhr.send(formData);

		    
		  },

	});