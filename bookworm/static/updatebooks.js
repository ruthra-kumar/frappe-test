//Global Data
records = [];

columns = [
    {name: 'bookid', type: 'number', header: 'Book ID', min: 1, modifiable: false,sortable: true},
    {name: 'title', type: 'text', header: 'Title', modifiable: true, sortable: true},
    {name: 'authors', type: 'text',header: 'Authors', modifiable: true, sortable: true},
    {name: 'isbn13', type: 'text',header: 'ISBN13', modifiable: true, sortable: true},
    {name: 'publication_date', type: 'date',header: 'Publication Date', modifiable: true, sortable: true},
    {name: 'publisher', type: 'text',header: 'Publisher', modifiable: true, sortable: true},
    {name: 'quantity', type: 'number',header: 'Quantity', modifiable: true, sortable: true},
];
table_options = {
    can_take_input: false,
    only_display: false,
};

tab1 = vuetable(records, columns, table_options);
tab1.$mount("#tableapp1");

var books_db = new Vue({
    el:'#updatebooks',
    data: {
    },
    methods: {
	savedb: function(){
	    var modified = tab1.getModifiedRecords();
	    var deleted = tab1.getDeletedRecords();
	    axios
		.post("http://127.0.0.1:5000/lms/updatebooks",{
		    modified_books: modified,
		    deleted_books: deleted,
		})
		.then(response => {
		    msg.add_messages(response.data['message'])
		})
	}
    },
    mounted: function() {
	var recs = records;
	axios
	    .get("/lms/listbooks")
	    .then(response => {
		tab1.table_records = response.data
	    })
    },
    
})
