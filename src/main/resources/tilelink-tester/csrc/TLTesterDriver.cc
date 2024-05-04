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
vector<uint64_t> req_types;
vector<uint64_t> addr_array;
vector<uint64_t> data_array;

vector<bool> used;

void read_line_to_array(string line, vector<uint64_t>& arr, int n_reqs, int base){
    string readval;
    stringstream ss(line);
    while (ss.good()) {
        getline(ss, readval, ',');
        arr.push_back(stol(readval, nullptr, base));
    }
    assert((arr.size()==n_reqs) && "Improper file format: num reqs does not match length");
}

extern "C" void init(int max_inflight) {

    printf("begin init\n");

    // Read in test data file
    string test_file;
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

    // Read in request data arrays
    getline(f, line);
    read_line_to_array(line, req_types, n_reqs, 10);
    cout << "req_types: " << req_types.size() << "\n";
    getline(f, line);
    read_line_to_array(line, addr_array, n_reqs, 16);
    cout << "addr_array: " << addr_array.size() << "\n";
    getline(f, line);
    read_line_to_array(line, data_array, n_reqs, 10);
    cout << "data_array: " << data_array.size() << "\n";

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
        cout << "Recieved RESP " << resp_idx << " --- data=" << resp_data << ", id=" << resp_id << ", write=" << req_types[resp_idx] << "\n";
        // cout << "resp_valid: " << resp_valid << "\n";
        // bool check = resp_valid == 0;
        // cout << "resp_valid==0: " << check << "\n";
        if (!req_types[resp_idx]) { //If outstanding request was a read 
            assert((resp_data == data_array[resp_idx]) && "Response data does not match request");
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
        *req_addr = addr_array[req_idx];
        *req_data = data_array[req_idx];
        *req_is_write = req_types[req_idx];
        *req_id = next_id;
        //cout << "Setting used\n";
        used[next_id] = true;
        cout << "Sending REQ " << req_idx << " --- addr=0x" << hex << addr_array[req_idx] << dec << ", data=" << data_array[req_idx] << ", write=" << req_types[req_idx] << ", id=" << next_id << "\n";
    }

    //cout << "req id: " << *req_id << "\n";

    *done = (resp_idx == (n_reqs - 1));

    //cout << "reached end\n";
}
