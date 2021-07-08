//Global Data
var records = [];

var columns = [
    {name: 'bookid', type: 'number', header: 'Book ID', min: 1, modifiable: false, sortable: true, modifiable: false},
    {name: 'title', type: 'text', header: 'Title', modifiable: true, sortable: true},
    {name: 'authors', type: 'text',header: 'Authors', modifiable: true, sortable: true},
    {name: 'isbn13', type: 'text',header: 'ISBN13', modifiable: true, sortable: true},
    {name: 'publication_date', type: 'date',header: 'Publication Date', modifiable: true, sortable: true},
    {name: 'publisher', type: 'text',header: 'Publisher', modifiable: true, sortable: true},
    {name: 'quantity', type: 'number',header: 'Quantity', modifiable: true, sortable: true},
];
var table_options = {
    only_display: true,
    can_take_input: false,
};


tab1 = vuetable(records, columns, table_options);
tab1.$mount("#tableapp1");

var addbooks = new Vue({
    el:'#addbooks',
    data: {
	newEntry: {
	    bookid: 1,
	    title: '',
	    authors: '',
	    isbn13: '',
	    publication_date: '1991-01-12',
	    publisher: '',
	    quantity: 10,
	},
    },
    methods: {
	savedb: function(){
	    var books = tab1.getNewRecords();
	    axios
		.post("/lms/addbooks",{
		    newbooks:  books
		})
		.then(response => {
		    msg.add_messages(response.data['message']);
		})
	},
	addEntry: function(){
	    var newBook = Object.assign({}, this.newEntry);
	    var table = this.tab1;
	    tab1.table_records.push(newBook);
	}
    }
});
