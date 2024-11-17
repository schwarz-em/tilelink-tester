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

    //AILSA'S CODE
    all_vals.reserve(n_reqs*3);

    for (int i =0; i < n_reqs; i++)
    {   
        getline(f, line);
        std::string readval;
        std::stringstream ss(line);
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 10));
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 16));
        getline(ss, readval, ',');
        all_vals.push_back(stol(readval, nullptr, 10));
    }
    //AILSA'S CODE

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
