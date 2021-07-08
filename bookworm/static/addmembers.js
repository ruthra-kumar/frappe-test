//Global Data
var records = [
];

var columns = [
    {name: 'memberid', type: 'number', header: 'Member ID', min: 1, sortable: true, modifiable: false},
    {name: 'first_name', type: 'text', header: 'First Name', sortable: true},
    {name: 'last_name', type: 'text',header: 'Last Name', sortable: true},
    {name: 'emailid', type: 'text',header: 'Email ID', sortable: true},
    {name: 'created_on', type: 'date',header: 'Created On', sortable: true},
];
var table_options = {
    can_take_input: false,
    only_display: true,
};


tab1 = vuetable(records, columns, table_options);
tab1.$mount("#tableapp1");

var books_db = new Vue({
    el:'#addmembers',
    data: {
	newEntry: {
	    memberid: 1,
	    first_name: '',
	    last_name: '',
	    emailid: '',
	    created_on: '1991-01-12',
	    amount_due: 10,
	},
    },
    methods: {
	addEntry: function(){
	    var newBook = Object.assign({}, this.newEntry);
	    var table = this.tab1;
	    tab1.table_records.push(newBook);
	},
	savedb: function(){
	    var members = tab1.getNewRecords();
	    axios
		.post("/lms/addmembers",{
		    newmembers:  members
		})
		.then(response => {
		    msg.add_messages(response.data['message']);
		})
	}
    }
});
