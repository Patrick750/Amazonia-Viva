const axios = require('axios');
const FormData = require('form-data');
const form = new FormData();
form.append('test', '123');

console.log("If you set Content-Type manually, the boundary is missing in the browser. In Node, form-data handles it, but in the browser it breaks.");
