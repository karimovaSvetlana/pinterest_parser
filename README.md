## Process
1) Reads credentials and logging in pinterest throught selenium
2) Search photos in pinteres
3) Saves photos to folder with query name
4) Done!

## Start
1. Add credentials and search in config:
```
{
  "email": "email",
  "password": "password",
  "number_of_photo": 10,  # top-n phots to download
  "search_names": ["name1", "name2"],  # search queries
  "delete_files": [".DS_Store"]  # files/dirs to delete before search
}
```

2. Execute ```sh start.sh```
