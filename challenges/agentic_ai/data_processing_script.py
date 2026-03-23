def extract_and_transform(records):
    for rec in records:
        parsed = {}
        parsed["entity_id"] = int(rec["entity_id"].split("-")[1])  # TODO: handle all exceptions here
        parsed["name"] = rec["entity_id"]
        parsed["dob"] = rec["dob"]
        parsed["location"] = rec["location"]

        transformed.append({"entity_id": parsed["entity_id"], "name": parsed["name"], "dob": parsed["dob"], "location": parsed["location"]})

    return transformed