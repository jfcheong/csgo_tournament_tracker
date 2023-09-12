import json


def load_events():
    with open('../../CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    return json_list


def extract_sample(full_events, event_id_list, sample_file_name):
    sample_events_list = []
    for i in range(4, len(full_events) - 1):
        loaded_events = json.loads(full_events[i])
        for j in range(len(loaded_events["events"])):
            if loaded_events["events"][j]["id"] in event_id_list:
                sample_events_list.append(loaded_events)

    with open(f'./{sample_file_name}', 'w') as file:
        json.dump(sample_events_list, file)

    print('Successfully extracted and saved sample events!')


def verify_extraction(event_id_list, sample_file_name):
    list_len = len(event_id_list)

    with open(f'./{sample_file_name}', 'r') as jsonl_file:
        json_list = json.load(jsonl_file)
    sample_file_len = sum(1 for line in json_list)

    print(list_len)
    print(sample_file_len)
    if list_len == sample_file_len:
        print("Verified to be successful")
    else:
        print("Verification failed, please rerun sample extraction")


r2_eid_preround_list = ['3bb88790-d6b5-4944-b6df-b3663330c2ff', '0333e6f5-dd8e-4f93-9dca-713fd474695a', '1b9802ec-a935-42c0-8396-83a7a3768d2c', 'e2f57ccd-7882-4337-b125-b203a398721e', '3b1adf9f-98d2-49dd-94e8-09c51ef027a9', 'f730a1d1-0010-40cf-8e2c-ec451eaf23e5', '4dcecb0d-d074-4004-a22a-a7c1167c44e1', '8d4634cf-5a90-4938-8f57-dd94f301c0bd', 'c785ed45-9b12-4b7f-851c-465cdd4f8f3a', 'a93a5dab-2f6f-44d6-8355-419d4f5f1ba9', '73ac03f3-795b-4bf9-9543-7baad884b1fc', '81d78168-4c61-4a00-9a1c-b95046aaf555', 'cd454282-eadb-414f-81b6-04c2b3c91672', 'dbdad42d-249b-4836-a92f-7537231ac3cd', '627fda3c-4b57-44ea-8b65-2aae7b8ddd24', 'b9d37c61-9c72-471e-a314-781e64bd9d7a', 'c5f4d3df-917d-4380-beae-781d5b44886e', '2a798fd8-ed28-4499-a4b5-54f625ef31bc', '2450b615-96ee-4976-bc44-4a7955f0f5b9', 'dfbeef63-5409-4042-903a-61df4ae781b1', '03a2192e-c944-4a4e-8c41-ccb06c7689c4', '5f5e35fe-f6a1-4b63-b8b1-b92a9afc998f', 'f3063898-4623-40fb-910f-c2f8e1d23df3', '52df1aab-56e3-4f66-8732-e8e395ee76ba', 'ce313124-1405-4a9e-a248-cc839e6a338d', '3e7a2aa0-8994-488c-9f8e-8d7738353505', 'de27aec6-390d-49f0-a1c5-88b6f30e15ea', 'e2a29785-581a-43d4-85f2-3dfce662b8e0', 'a8c2295a-f565-47de-b517-6465e7d9cf45', 'e8cfb874-ec5b-41aa-b84f-18779c08d5e4', '36b87756-c525-4a75-8fc9-9b23c537239e', '1fa384b9-3240-45f4-b2b4-35aaad22231c', 'e2963b00-59b5-472b-9ea6-f02058cf2fc8', 'bc2a2712-6411-45e9-b477-866135d32a3f', '730cc28f-30a5-49e7-b4d2-7057def37b63', '9a20a001-0651-4975-b44a-220a79fa03d7', 'e174fb6d-5805-4017-b0e4-8eb838a09a91', '386b208e-0f7d-4f02-9e1e-bba07a6119ab', 'ab15d1bc-07b9-46ad-80bb-70570fdd02f6', 'de9cd0dc-cb88-4e1f-b957-090af7b09526', '674ff49f-baea-4c7c-9372-47e8dbf51fc4', 'b60c977d-cf69-4692-b085-19d52197a996', '8ad25215-de7c-4952-a230-3451d864338f', 'e2ccacdf-eb4c-4a53-bc05-5713663b1ce4', 'e5d3b97f-383a-4852-9b5c-41dc88259175', '44886978-2456-4e5f-b4a7-8dd0585242bf', '76ee59b9-b29c-4943-ab10-3e73ed326d0a', '0ea59f6d-a7f9-4bf6-b6db-293257fcd9eb', '69417807-8303-4ea4-85a5-43907e449b5e', '90ee06fb-6ee9-4a25-a819-4893e7a76d8e', '3d380ecc-85b8-41d2-9ac3-fc15c8b213e3', '8c9e6e89-f6b3-42e1-b107-050ece4bae83', 'de71caac-3994-4743-8761-5a4300ae9878', '030fd441-9d0c-4177-810a-30051ed4644c', '22963536-2a91-458e-bb6e-0cc83f06a19f', '1ce3128c-9e4f-41ef-8f3a-b0122630b89f', 'a54390fd-0e49-4bef-8567-22d71d162423', '008ee0f5-3fdc-4d3c-844b-5e1490368883', '17cfd64d-d40a-4300-8c53-4922f7a42ea3', '90c9856c-23e2-4bdd-8996-79ba39c3898b', 'fe57157a-3e43-43ce-a5c5-1356d5096d59', '2aa79c3c-eab6-4f80-b249-a4887abb3b16']
r2_eid_duringround_list = ['8ea82f8b-ab45-42fb-9cb1-fe90b8246923', 'd9e7735d-ea9d-41a5-9971-dc77178bec1c', '8c062b3b-624c-422c-9997-631f2b4ee045', 'c99091fb-e18b-418e-a93d-6338907b084a', 'f087de43-8f01-4dc9-9c79-13339454db95', 'eff4e72c-be30-4b8b-9bf9-3fe5661dad64', '0f21b4f6-e31b-46aa-8377-a3bed7dacfe5', '82c5dd64-d0f6-4413-b156-d0ce28fb49e2', 'bf5ce6c6-86ef-49bb-9bbe-690dafd33e42', 'fff8c15a-7868-44ba-a036-947e3766d07c', '42fbeada-e083-4bcc-80f8-a307a9aca72e', '83e93b43-07cc-4c0f-b656-4b208a8d1ba8', '13d1a95e-e5de-4d00-839e-a10ae7c77ea6', '1a6d5931-4fe1-446d-941d-86127bf2da1c', '50de27c8-01ff-45d3-a143-8baa80d695b0', '2457f7de-daf8-4f48-9bb2-6984934aa4c2', 'e532466a-d9cd-47c0-97b6-ec85d97c96a3', '07ed236d-baf7-4fab-9f49-2f5bcb6367d7', '83519a60-6fb3-4c2e-96f9-460c1acb2472', '3eb6828d-9664-4329-b46d-f355b564fb36', '899c5157-fbc8-46ae-9df3-cc9b09f896f6', 'f52dd77a-61e5-4ccd-8da9-0385976d76ac', 'c3b0483b-eda2-41b2-915a-fffceb922753', '4788a6e8-5f26-4288-bf74-801706f92420', 'cdafb888-e229-47b7-9bda-16fd61bd17ee', 'ad23a32d-86a1-4111-b48d-60fd76ac4fe3', '77c655a9-9c9b-4360-8cde-cbe0845af218', '7733512a-5af9-4a87-9042-e9a941f05be9', '8834adc2-860a-4db5-8003-ae6fd0841d52', '5fb13435-db10-4ad9-83a1-1eda7ee0600d', 'ae5b61b9-e085-4379-a5f4-b1ca453884fe', '9c13a7aa-fd4d-45b9-9749-f4fd05c5df78', 'c6d785dc-dad7-4662-b954-097bad9358d8', 'aa111fe9-2f69-4c42-a694-d51e244711b4', 'c9ce9c60-31b1-4b2e-81d9-97165f403483', 'aa0d2e15-5dfb-4497-9bf3-3b348eec6a18', '9e92ba48-85ae-4ee1-9c48-e17f9672de0e', 'b9cc15f5-715e-4449-ad70-555cd46c34e8', '34007943-82c5-4c23-8944-6a35e8912a19', '8f198336-d4ea-474c-8f9f-348e72a32716', '6b92fce7-f1e0-4370-8d6b-90ad4ccab9d2', '70a3b8d1-850c-4873-96c6-65e7ca7a6f91', '47f945d5-d6aa-4c4f-b985-b707ae7cc7c3', '7f729958-b458-4b84-8b77-1b2bc3d1faa3', 'f899d072-55b3-49b4-95c3-437b1d5c5eb7', '4bf81491-e158-4f8b-81b4-1c6216b87562', 'bea49019-eaac-418a-b05d-3c853a4fb4d0', '011b621f-e6c0-4465-859e-3af42e240f94', '6d4bc6f5-4747-49e7-a70f-0f6737290bfb', '50d292a7-264c-439b-a28b-2f0584f70ca8', '82b8e917-1376-468a-9f87-50f65fa13e44']
r2_eid_list = r2_eid_preround_list + r2_eid_duringround_list

# end_eid_list = ['f35471b7-952c-4efe-b847-80bb74ce8c2a', '82b8e917-1376-468a-9f87-50f65fa13e44', '54c504b3-e884-42ae-a751-9d5d66979cb3', '4f7e43dc-9bc2-4797-9ae8-ab30ee5a8bf6', '721b1669-b752-4b26-90cc-78f039f2c02e', 'e1cd7ef1-4744-4376-9293-b75fdd4bdd35', '7a5c9cf9-390f-44d4-b8a6-ec99b7ab73df', 'aec88b6c-9afe-41f8-8d52-1f1745825eef', '7bbfe100-6607-4f47-b30c-cfbcccce1276', '6232d134-4705-46d4-8b51-4920e4c7aad8', '1d57300e-f914-4109-9dcb-23469081586e', 'e9ca6127-6096-4455-8a7c-d0c2fa0fd2bd', '3bb18309-38ee-49c8-bac8-cc65eea7ba23', 'd868ff25-1a71-4336-92a6-4493520a0d40', '7c465bfe-d26f-40c5-ad6e-1c14305a8d55', 'd2ba3c87-125f-417c-aeed-ab248bdbbc07', '67d5b7d4-3cfb-4436-a1fe-f0750c1b0892', 'd72c5112-c009-4f10-ae78-6b4ba2e12dee', '1018abaa-1661-49ee-aa05-43db25b24527', '71c9eac9-171e-47af-9561-0a2b56067ccd', '5c29d456-1554-433b-9cb2-6d8f94e9c1a2', 'c6e41b6c-44f6-42e3-955d-588195e651c2', 'ecc3a49b-240d-4158-a496-909bd8e8d9f9', '05c53fad-d9e0-40ba-bb7c-d9c77649bbf6', '636217c7-f89a-4a3f-a5ed-5b76d5cfad6e', 'c736ed6d-1e86-418e-aebc-36540de9589e', 'cae04355-c61e-47ac-8828-162a3f95603b', '57a73440-d072-48e6-84f6-f84ca993263f', '687d4c0d-e3a5-43b2-a2b6-dd1412bd0d3e', 'b9c21f92-b5ab-4041-b431-34b817096bc8', '572c5102-aa0d-475c-9238-cd4a716dd08e', '6e857943-58dd-48d5-a42c-1fb6229a4551', 'd15804de-5398-4b4a-a6d5-d1230b8be859', '54803850-bc97-49c7-97c9-c55293e76d09', '497434b0-21de-4b60-ab8d-8063eab130ff', 'c6d41c5a-a04b-4586-a219-6d8172a3ea84', '53697a71-b14a-4849-8b78-fb88394c35a0', '875e969c-328d-4606-825c-445625f005cc', '63612aca-83f1-4745-9b79-9259b6067ce0', '39a61ab4-7475-45fc-9599-6a700e898ced', 'b447cc29-d133-44e5-b116-a960f4fe9ab4', 'bcd2fe49-106f-4aa2-8bea-1d8f2257c000', '2348dbb1-053a-41ad-9cb5-0256eb09ab14', '4c41bc08-a590-45bc-b418-118c7ca6f9f6', 'a8ca863a-5d83-4761-9a88-4e69deaa2ebe', '42c5d10b-9835-4f86-b62b-c9d4c1c101dc', '203b0896-3f9e-4768-8631-28bcc13ce760', '294ccf13-cdd7-4bd5-81e3-98b76b215672', '79fb2e1b-c201-429b-b1ca-e3bcd17f9f56', 'f9852911-f659-46da-91e3-e4da9654a238', 'c5ccdc67-26e7-46ce-b1f4-1c71cb774117', 'e2d7672e-87c2-4beb-9e27-4af70b17c5f7', '18402283-9873-448e-8b91-a316dedd1ee8']

full_events = load_events()

extract_sample(full_events, r2_eid_list, '../2579089_events_round_2_sample.jsonl')

verify_extraction(r2_eid_list, '../2579089_events_round_2_sample.jsonl')
