//Global Data for issued books table
var issue_form = new Vue({
    el:'#bookissue',
    data:{
	searchBook: "",
	searchMember: "",
	books: [],
	members: [],
	selectedBook: "",
	selectedMember: "",
	issueDate: "",
    },
    created: function(){
	//Get Books and Memers from server
	axios
	    .get('/lms/get_issueform_data')
	    .then(response => {
		this.books = response.data['books'],
		this.members = response.data['members']
	    });

    },
    methods: {
	issueBook: function(){
	    selBook = this.selectedBook;
	    selMember = this.selectedMember;
	    issueDate = this.issueDate;
	    
	    if(selBook == "" || selMember == ""){
		msg.add_messages(['Select Book and Member']);
	    }
	    else{
		axios
		    .post('/lms/issuebook',{
			selected_book: selBook,
			selected_member: selMember,
			issueDate: issueDate
		    })
		    .then(response => {
			msg.add_messages(response.data['message']),
			this.books = response.data['books'],
			this.members = response.data['members']
		    })
	    }
	},
    },
    computed: {
	filteredBooks: function(){
	    var bks = this.books;
	    var query = this.searchBook;
	    if (query != ""){
		return bks.filter(function(elem){
		    return (elem.title.toLowerCase().includes(query.toLowerCase()) || elem.bookid.toString().includes(query));
		})
	    }
	    else
		return bks;
	},
	filteredMembers: function(){
	    var mems = this.members;
	    var query = this.searchMember;
	    if (query != ""){
		return mems.filter(function(elem){
		    return (elem.first_name.toLowerCase().includes(query.toLowerCase()) || elem.last_name.toLowerCase().includes(query.toLowerCase()) || elem.memberid.toString().includes(query));
		})
	    }
	    else
		return mems;
	}
    }
})
