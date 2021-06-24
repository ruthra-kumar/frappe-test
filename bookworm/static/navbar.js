//Change Navigation bar Node width based on 'collapsed' parameter
var collapsed = false;
function handle_navbar_collapse(){
    collapsed = !collapsed;
    doc = document.getElementById('document');
    if(collapsed){
	doc.style.gridTemplateColumns = "0.8em auto";
    }
    else {
	doc.style.gridTemplateColumns = "14% 86%";
    }

}

navbar = new Vue({
    el: '#navbar',
    data: {
	collapse_sign: "«",
	expand_sign: "»",
	navbar_height: "",
    },
    mounted: function(){
	navbar_height = parseInt(window.getComputedStyle(this.$el).height);
	this.$refs.navbar_btn_text.style.top = (Math.min(window.innerHeight, navbar_height)/2).toString() + 'px';	
    },
    methods: {
	handle_expand_btn: function(event) {
	    navbar_height = parseInt(window.getComputedStyle(this.$el).height);
	    
	    if(this.$refs.navbar_content.style.display == "none"){
		//Expand Navigation bar
		
		//Show navbar content
		this.$refs.navbar_content.style.display = "";

		//increse navbar's grid item width
		this.$el.style.gridTemplateColumns = "auto 0.8em";

		//some eye-candy changes
		this.$refs.navbar_btn.style.borderRadius = "0px 5px 5px 0px";

		//update button sign
		this.$refs.navbar_btn_text.textContent = this.collapse_sign;
	    }
	    else {
		//Collapse
		//Hide navbar content
		this.$refs.navbar_content.style.display = "none";
		//decrease navbar's grid item width
		this.$el.style.gridTemplateColumns = "0% 100%";
		//eye-candy changes
		this.$refs.navbar_btn.style.borderRadius = "5px"
		//update button sign
		this.$refs.navbar_btn_text.textContent = this.expand_sign;
	    }

	    this.$refs.navbar_btn_text.style.top = (Math.min(window.innerHeight, navbar_height)/2).toString() + 'px';

	    // Trigger the collapse on main grid
	    handle_navbar_collapse();
	}
    }
});
