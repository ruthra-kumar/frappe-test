//Global Data
var records = [];

let columns = [
    {name: 'bookid', type: 'number', header: 'Book ID', min: 1, modifiable: false, sortable: true},
    {name: 'title', type: 'text', header: 'Title', modifiable: true, sortable: true},
    {name: 'authors', type: 'text',header: 'Authors', modifiable: true, sortable: true},
    {name: 'isbn13', type: 'text',header: 'ISBN13', modifiable: true, sortable: true},
    {name: 'publication_date', type: 'date',header: 'Publication Date', modifiable: true, sortable: true},
    {name: 'publisher', type: 'text',header: 'Publisher', modifiable: true, sortable: true},
    {name: 'quantity', type: 'number',header: 'Quantity', modifiable: true, sortable: true},
];
let table_options = {
    only_display: true,
    can_take_input: false,
};


tab1 = vuetable(records, columns, table_options);
tab1.$mount("#tableapp1");

var frappe_library = new Vue({
    el:'#frappe-library',
    data: {
	param_title: "",
	param_author:"",
	param_isbn:"",
	param_publisher:"",
	param_book_count: 40,
	max_pages: 200,
	found_books: 0,
    },
    methods: {
	add_results_to_table: function(books){
	    let required_books = (this.param_book_count - records.length);
	    let bk = {};
	    let count = 0;
	    let newbooks = [];
	    if(required_books >= books.length){
		count = books.length;
	    }
	    else{
		count = required_books;
	    }
	    for(let x=0;x<count;x++){

		let key = books[x]
		let new_obj = {};
		bk.bookid = key.bookID;
		bk.title = key.title;
		bk.authors = key.authors;
		bk.isbn13 = key.isbn13;
		//Parse date into YYYY-MM-DD format
		bk.publication_date = new Date(Date.parse(key.publication_date));
		bk.publication_date = bk.publication_date.toLocaleString('fr-CA', { year: "numeric", month:"2-digit", day: "2-digit" });
		bk.publisher = key.publisher;
		bk.quantity = 10;
		
		newbooks.push(Object.assign(new_obj,bk));
	    }
	    records.splice(records.length, 0, ...newbooks);
	},
	query_frappe_api: function(){
	    var url = "/lms/proxy_frappe_api";
	    var current_page = 1;
	    records.splice(0);
	    let required_pages = ((this.param_book_count/20) >= this.max_pages) ? this.max_pages: (this.param_book_count/20)+1;
	    for(;current_page <= required_pages; current_page++){
		axios
		    .get(url,{
			params: {
			    title:this.param_title,
			    author:this.param_author,
			    isbn:this.param_isbn,
			    publisher:this.param_publisher,
			    page:current_page,
			}
		    }, {
			Origin: 'https://frappe.io',
		    })
		    .then( response => { //All ok
			let books = response.data.message;
			if(books.length > 0){
			    this.add_results_to_table(books);
			    msg.feedback = "Loading " + current_page;
			}
			else{
			    current_page = required_pages+1;
			}
		    })
	    }
	    msg.feedback = records.length + " Books found";
	},
	save_to_db: function(){
	    var books = tab1.getNewRecords();
	    axios
		.post("/lms/addbooks",{
		    newbooks:  books
		})
		.then(response => {
		    msg.messages = response.data;
		})
	}
    }
})
