//Global Data
records = [];

columns = [
    {name: 'memberid', type: 'number', header: 'Member ID', min: 1, sortable: true, modifiable: false},
    {name: 'first_name', type: 'text', header: 'First Name', sortable: true, modifiable: true},
    {name: 'last_name', type: 'text',header: 'Last Name', sortable: true, modifiable: true},
    {name: 'emailid', type: 'text',header: 'Email ID', sortable: true, modifiable: true},
    {name: 'created_on', type: 'date',header: 'Created On', sortable: true, modifiable: true},
];
table_options = {
    can_take_input: false,
    only_display: false,
};

tab1 = vuetable(records, columns, table_options);
tab1.$mount("#tableapp1");

var books_db = new Vue({
    el:'#updatemembers',
    data: {
    },
    methods: {
	savedb: function(){
	    var modified = tab1.getModifiedRecords();
	    var deleted = tab1.getDeletedRecords();
	    axios
		.post("/lms/updatemembers",{
		    modified_members: modified,
		    deleted_members: deleted,
		})
		.then(response => {
		    msg.add_messages(response.data['message'])
		    if(response.data['deletion_opr'] == 'Success'){
			tab1.resetDeletionTracker();
		    }

		    if(response.data['update_opr'] == 'Success'){
			tab1.resetModificationTracker();
		    }

		})
	}
    },
    mounted: function() {
	var recs = records;
	axios
	    .get("/lms/listmembers")
	    .then(response => {
		tab1.table_records = response.data
	    })
    },
});
