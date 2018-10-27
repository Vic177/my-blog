$(document).ready(function(){
	$(".to-comment button").click(function(){
		$(this).parents(".comment").siblings().find("form.commentform").hide();//
		$(this).parents(".comment").siblings().find("form.replyform").hide();//
		$(this).parents(".comment-footer").siblings(".replies").find("form.replyform").hide();
		$(this).parents(".comment-footer").siblings("form").toggle();
	});
});

$(document).ready(function(){
	$(".to-reply button").click(function(){
		$(this).parents(".comment").siblings().find("form.commentform, form.replyform").hide();//
		$(this).parents(".comment").find("form.commentform").hide();//
		$(this).parents(".reply").siblings().find("form.replyform").hide();//
		$(this).parents(".reply-footer").siblings("form").toggle();
	});
});

$(document).ready(function(){
	$(".to-message button").click(function(){
		$(this).parents(".message").siblings().find("form.comment-message").hide();
		$(this).parents(".message-footer").siblings("form").toggle();
	});
});

$(document).ready(function(){
	$(".dialogue button").click(function(){
		$(this).parents(".comment-footer").siblings(".replies").toggle();
	});
});

