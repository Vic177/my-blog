$(document).ready(function(){
	$(".dialogue button").click(function(){
		$(this).parents(".comment-footer").siblings(".replies").toggle();
	});
});


$(document).ready(function(){
	$(".post-op").mouseover(function(){
		$(this).find(".op").css("display","block")
	});
	$(".post-op").mouseout(function(){
		$(this).find(".op").css("display","none")
	});
});