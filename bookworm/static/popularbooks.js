//Global Data
let table_options = {
    can_take_input: false,
    only_display: true,
};

let popular_books = [];

let books_columns = [
    {name: 'bookid', type: 'text', header: 'Book ID', sortable: true},
    //{name: 'holders', type: 'text',header: 'Holders', sortable: true},
    {name: 'title', type: 'text', header: 'Title', min: 1, sortable: true},
    {name: 'authors', type: 'text',header: 'Authors', sortable: true},
    {name: 'available_quantity', type: 'text',header: 'Available Quantity', sortable: true},
    {name: 'total_quantity', type: 'text',header: 'Total Quantity', sortable: true},
];

tab1 = vuetable(popular_books, books_columns, table_options);
tab1.$mount("#books");

var getdata = new Vue({
    el: '#getdata',
    data: {
	books: [],
    },
    created: function(){
	var books = this.books;
	var formatted_data = [];
	axios
	    .get('/lms/popularbooks')
	    .then(response => {
		books = response.data['books']
		formatted_data = this.build_popular_books_report(books);
		popular_books.splice(0);
		popular_books.splice(0,0, ...formatted_data);

	    })
    },
    methods: {
	build_popular_books_report: function(data){
	    let report_data = [];
	    data.forEach(elem => {
		report_data.push(
		    {
			bookid: elem.bookid,
			title: elem.title,
			authors: elem.authors,
			available_quantity: elem.available_quantity,
			total_quantity: elem.total_quantity,
		    }
		);
	    });
	    return report_data;
	},
	getData: async function(){
	    //Get data for the most popular books
	    response = await axios.get('/lms/popularbooks')
	    if(response.status == '200'){
		this.books = response.data['books'],
		msg.messages = response.data['message']
	    }else{
		msg.messages = 'Network error'
	    }
	    
	    formatted_data = this.build_popular_books_report(this.books);
	    popular_books.splice(0);
	    popular_books.splice(0,0, ...formatted_data);
	}
    }
});
