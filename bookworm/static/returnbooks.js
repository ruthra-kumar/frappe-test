//Global Data for issued books table
var issued_books = [];
var unpaid_returns = [];

var columns = [
    {name: 'transactionid', type: 'text', header: 'Transaction', sortable: true, modifiable:false},
    {name: 'member', type: 'text', header: 'Member',  sortable: true, modifiable:false},
    {name: 'book', type: 'text', header: 'Book', sortable: true, modifiable:false},
    {name: 'issued_date', type: 'date',header: 'Issued Date', sortable: true, modifiable:false},
    {name: 'returned_date', type: 'date',header: 'Returned Date', sortable: true, required: true, modifiable:true, dependents: {column: 'rent_fee', func: function(record){
	var took_on = new Date(record.issued_date);
	var returned_on = new Date(record.returned_date);
	var holding_period = returned_on.getTime() - took_on.getTime();
	days = (holding_period/1000/60/60/24);
	record.rent_fee = ((days > 30) ? ((days - 30) * 1 > 100 ? 100 : (days - 30) * 1 ): 0);
    }}},
    {name: 'rent_fee', type: 'number',header: 'Rent Fee', sortable: true, required: true, modifiable:false},
    {name: 'paid', type: 'checkbox',header: 'Paid?', sortable: true, required: true, modifiable:true},
];

var table_options = {
    can_take_input: false,
    only_display: false,
};

var columns2 = [
    {name: 'transactionid', type: 'text', header: 'Transaction',  sortable: true, modifiable: false},
    {name: 'member', type: 'text', header: 'Member',  sortable: true, modifiable: false},
    {name: 'book', type: 'text', header: 'Book', sortable: true, modifiable: false},
    {name: 'issued_date', type: 'date',header: 'Issued Date', sortable: true, modifiable: false},
    {name: 'returned_date', type: 'date',header: 'Returned Date', sortable: true, required: true, modifiable: false},
    {name: 'rent_fee', type: 'number',header: 'Rent Fee', sortable: true, required: true, modifiable: false},
    {name: 'paid', type: 'checkbox',header: 'Paid?', sortable: true, required: true, modifiable: true},
];

issuedBooks = vuetable(issued_books, columns, table_options);
issuedBooks.$mount("#issuedbooks");

unpaidreturn = vuetable(unpaid_returns, columns2, table_options);
unpaidreturn.$mount("#unpaidreturn");

var book_return = new Vue({
    el:'#bookreturn',
    data: {
	transactions: [],
	unpaid_transactions: [],
    },
    created: function(){
	this.getAllTransactions();
    },
    methods: {
	build_issued_table: function(issued_books){
	    //Build table data for the return form table
	    var tab_issued_books = [];
	    this.transactions = issued_books;
	    issued_books.forEach(function(elem){
		tab_issued_books.push({
		    transactionid: elem.transactionid,
		    memberid: elem.member.memberid,
		    member: elem.member.first_name + ' ' + elem.member.last_name,
		    bookid: elem.book.bookid,
		    book: elem.book.title,
		    issued_date: elem.issued_date,
		    rent_fee: 0,
		})})
	    return tab_issued_books;
	},
	build_unpaid_table: function(unpaid_returns){
	    //Build table data for the return form table
	    var tab_unpaid_books = [];
	    this.unpaid_transactions = unpaid_returns;
	    unpaid_returns.forEach(function(elem){
		tab_unpaid_books.push({
		    transactionid: elem.transactionid,
		    memberid: elem.member.memberid,
		    member: elem.member.first_name + ' ' + elem.member.last_name,
		    bookid: elem.book.bookid,
		    book: elem.book.title,
		    issued_date: elem.issued_date,
		    returned_date: elem.returned_date,
		    rent_fee: elem.rent_fee,
		})})
	    return tab_unpaid_books;
	},	    
	getAllTransactions: function(){
	    msg.add_messages([])

	    axios
		.get('/lms/getIssued')
		.then(response => {
		    let transaction_data = this.build_issued_table(response.data);
		    issued_books.splice(0);
		    issued_books.splice(0,0,...transaction_data);
		})

	    //Get unpaid returns
	    axios
		.get('/lms/getUnpaid')
		.then(response => {
		    let transaction_data = this.build_unpaid_table(response.data);
		    unpaid_returns.splice(0);
		    unpaid_returns.splice(0,0,...transaction_data);
		})
	    
	},
	issueReturn: function(){
	    let selected = issuedBooks.getModifiedRecords();

	    let returned_books = [];
	    selected.forEach(function(elem){
		returned_books.push({
		    transactionid: elem.transactionid,
		    returned_date: elem.returned_date,
		    rent: elem.rent_fee,
		    paid: elem.paid,
		});
	    });

	    axios
		.post('/lms/issuereturn',{
		    returned_books: returned_books
		})
		.then(response=>{
		    msg.add_messages(response.data['message'])
		})
	},
	payDebt: function(){
	    let selected = unpaidreturn.getModifiedRecords();

	    let paid_books = [];
	    selected.forEach(function(elem){
		paid_books.push({
		    transactionid: elem.transactionid,
		    paid:  elem.paid,
		});
	    });

	    axios
		.post('/lms/payDebt',{
		    paid_books: paid_books
		})
		.then(response=>{
		    msg.add_messages(response.data['message'])
		})
	}
    }
});
