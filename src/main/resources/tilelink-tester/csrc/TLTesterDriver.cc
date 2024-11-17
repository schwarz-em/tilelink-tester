#include <vpi_user.h>
#include <svdpi.h>
#include <stdint.h>
#include <cassert>
#include <fstream>
#include <vector>
#include <iostream>
#include <sstream>
#include <cstring>
using namespace std;

int req_idx;
int resp_idx;
int last_valid;

int n_reqs;
//AILSA'S CODE
vector<uint64_t> all_vals;
//AILSA'S CODE
vector<uint64_t> req_types;
vector<uint64_t> addr_array;
vector<uint64_t> data_array;

vector<bool> used;

<<<<<<< Updated upstream
void read_item_to_array(string val, vector<uint64_t>& arr, int base){
    arr.push_back(stol(val, nullptr, base));
=======
void read_line_to_array(string line, vector<uint64_t>& arr){
    // string readval;
    // stringstream ss(line);
    // while (ss.good()) {
    //     getline(ss, readval, ',');
    //     arr.push_back(stol(readval, nullptr, base));
    // }
    // assert((arr.size()==n_reqs) && "Improper file format: num reqs does not match length");

    std::string readval;
    std::stringstream ss(line);
    getline(ss, readval, ',');
    arr.push_back(stol(readval, nullptr, 10));
    getline(ss, readval, ',');
    arr.push_back(stol(readval, nullptr, 16));
    getline(ss, readval, ',');
    arr.push_back(stol(readval, nullptr, 10));
>>>>>>> Stashed changes
}

extern "C" void init(int max_inflight) {

    printf("begin init\n");

    // Read in test data file
    string test_file;
    test_file = "test_data.txt";
    s_vpi_vlog_info info;
    if (!vpi_get_vlog_info(&info))
      abort();
    for (int i = 1; i < info.argc; i++) {
      std::string arg(info.argv[i]);

      if (arg.find("+tltestfile=") == 0) {
        test_file = arg.substr(strlen("+tltestfile="));
      }
    }
    assert((test_file != "") && "Test file cannot be empty");

    ifstream f;
    string line;
    f.open(test_file);

    printf("opened file\n");

    // Read in number of requests to send
    getline(f, line);
    cout << line << "<-end\n";
    n_reqs = stoi(line, nullptr);

    cout << n_reqs << "\n";

<<<<<<< Updated upstream
    //AILSA'S EDITS BEGIN
    for (int i =0; i < n_reqs; i++)
    {
        getline(f, line);
       
        string readval;
        stringstream ss(line);
        while (ss.good()) {
            getline(ss,readval, 'v');
            read_item_to_array(readval, req_types, 10);
            getline(ss, readval, ',');
            read_item_to_array(readval, addr_array, 16);
            getline(ss, readval, ',');
            read_item_to_array(readval, data_array, 10);
        }
    }
    //AILSA'S EDITS END

    // // Read in request data arrays
    // getline(f, line);
    // read_line_to_array(line, req_types, n_reqs, 10);
    cout << "req_types: " << req_types.size() << "\n";
    // getline(f, line);
    // read_line_to_array(line, addr_array, n_reqs, 16);
    cout << "addr_array: " << addr_array.size() << "\n";
    // getline(f, line);
    // read_line_to_array(line, data_array, n_reqs, 10);
    cout << "data_array: " << data_array.size() << "\n";
=======
    // Read in request data arrays
   // getline(f, line);
    // read_line_to_array(line, req_types, n_reqs, 10);
    // cout << "req_types: " << req_types.size() << "\n";
    // getline(f, line);
    // read_line_to_array(line, addr_array, n_reqs, 16);
    // cout << "addr_array: " << addr_array.size() << "\n";
    // getline(f, line);
    // read_line_to_array(line, data_array, n_reqs, 10);
    // cout << "data_array: " << data_array.size() << "\n";

    //AILSA'S CODE
    all_vals.reserve(n_reqs*3);

    for (int i =0; i < n_reqs; i++)
    {   
        cout << i;
        getline(f, line);
        cout << line << "\n";

        std::string readval;
        std::stringstream ss(line);
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 10));
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 16));
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 10));

        //read_line_to_array(line, all_vals);
    }

    cout << "\n BREAK - NOW READING OUT ALL_VALS \n";

    int k = all_vals.size();
    for (int i = 0; i < k; i++) {
        cout << all_vals[i] << "\n";
    }
    //AILSA'S CODE
>>>>>>> Stashed changes

    req_idx = 0;
    resp_idx = 0;
    last_valid = 0;

    for (int i=0; i<max_inflight; i++) {
        used.push_back(false);
    }

    cout << "max inflight: " << max_inflight << "\n";
    cout << "used array size: " << used.size() << "\n";
}

//TODO: add reset?
extern "C" void tick(
    //IO to vlog       
    unsigned char *req_valid,
    unsigned char req_ready,
    long long int *req_addr,
    long int *req_data,
    long int *req_id,
    unsigned char *req_is_write,

    unsigned char resp_valid,
    long int resp_data,
    long int resp_id,

    unsigned char *done
) {
    
    //cout << "tick\n";

    bool req_fire = last_valid && req_ready;
    if (req_fire) {
        cout << "req sent\n";
        req_idx = req_idx + 1;
    }

    // Should never recieve more responses than number of sent requests
    assert((resp_idx <= req_idx) && "More responses seen than requests");

    if (resp_valid) {
        cout << "Recieved RESP " << resp_idx << " --- data=" << resp_data << ", id=" << resp_id << ", write=" << all_vals[req_idx*3] << "\n";
        // cout << "resp_valid: " << resp_valid << "\n";
        // bool check = resp_valid == 0;
        // cout << "resp_valid==0: " << check << "\n";
        if (!all_vals[resp_idx*3]) { //If outstanding request was a read 
            assert((resp_data == all_vals[resp_idx*3+2]) && "Response data does not match request");
        }
        resp_idx = resp_idx + 1;
        used[resp_id] = false;
    }

    uint64_t next_id = 0;
    while(next_id < used.size() && used[next_id]) {
        next_id++;
    }
    bool id_avail = next_id != used.size();
    //cout << "next id: " << next_id << "\n";
    //cout << "id avail: " << id_avail << "\n";

    // Send next request
    *req_valid = (req_idx < n_reqs) && id_avail;
    last_valid = *req_valid;
    if (*req_valid) {
        *req_addr = all_vals[req_idx*3+1];
        *req_data = all_vals[req_idx*3+2];
        *req_is_write = all_vals[req_idx*3];
        *req_id = next_id;
        //cout << "Setting used\n";
        used[next_id] = true;
        cout << "Sending REQ " << req_idx << " --- addr=0x" << hex << all_vals[req_idx*3+1] << dec << ", data=" << all_vals[req_idx*3+2] << ", write=" << all_vals[req_idx*3] << ", id=" << next_id << "\n";
    }

    //cout << "req id: " << *req_id << "\n";

    *done = (resp_idx == n_reqs);

    //cout << "reached end\n";
}
