$(document).ready(function(){
	$(".comment-footer button").click(function(){
		//当前元素父级元素.comment的同胞元素中子元素中的.comment-footer form隐藏
		$(this).parents(".comment").siblings().find(".comment-footer form").hide();
		//当前元素父级元素.comment的同胞元素中子元素中的.reply-date form隐藏
		$(this).parents(".comment").siblings().find(".reply-date form").hide();
		//当前元素父级元素.comment的子元素中的.comment-footer form隐藏
		$(this).parents(".comment").find(".reply-date form").hide();
		$(this).siblings(".comment-footer form").toggle("fast");
	});
});

$(document).ready(function(){
	$(".reply-date button").click(function(){
		//当前元素父级元素.comment的子元素中的.comment-footer form隐藏
		$(this).parents(".comment").find(".comment-footer form").hide();
		//当前元素父级元素.comment的同胞元素中子元素中的.comment-footer form隐藏
		$(this).parents(".comment").siblings().find(".comment-footer form").hide();
		//当前元素父级元素.comment的同胞元素中子元素中的.comment-footer form隐藏
		$(this).parents(".comment").siblings().find(".reply-date form").hide();
		//当前元素父级元素.reply的子元素中的.reply-date form隐藏
		$(this).parents(".reply").siblings().find(".reply-date form").hide();
		$(this).siblings(".reply-date form").toggle("fast");
	});
});