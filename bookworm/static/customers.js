//Global Data
var paying_customers = [];

var customers_columns = [
    {name: 'memberid', type: 'text', header: 'Member ID', sortable: true},
    {name: 'name', type: 'text', header: 'name', min: 1, sortable: true},
    {name: 'paid', type: 'number',header: 'Paid', sortable: true},
];
var table_options = {
    can_take_input: false,
    only_display: true,
};

tab1 = vuetable(paying_customers, customers_columns, table_options);
tab1.$mount("#customers");

var getdata = new Vue({
    el: '#getdata',
    data: {
	customers: [],
    },
    created: function(){
	var customers = this.customers;
	axios
	    .get('/lms/getCustomers')
	    .then(response => {
		customers = response.data['customers']
		formatted_data = this.build_customers_report(customers);
		paying_customers.splice(0);
		paying_customers.splice(0,0, ...formatted_data);
	    });
    },
    methods: {
	build_customers_report: function(data){
	    var report_data = [];

	    data.forEach(elem => {
		report_data.push(
		    {
			memberid: elem.memberid,
			name: elem.first_name + " " + elem.last_name,
			paid: elem.paid,
		    })});
	    return report_data;
	},
	getData: async function(){
	    //Get data for the highest paying customer
	    var formatted_data;
	    var response = await axios.get('/lms/getCustomers')
	    if(response.status == '200'){
		this.customers = response.data['customers'],
		msg.add_messages(response.data['message'])
	    }else{
		msg.add_messages(['Network error'])
	    }
	    
	    formatted_data = this.build_customers_report(this.customers);
	    paying_customers.splice(0);
	    paying_customers.splice(0,0, ...formatted_data);
	}
    }
})
