from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["organization", "person", "geo", "event", "category"]

PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"

PROMPTS["entity_extraction"] = """---Goal---
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
Use {language} as output language.

---Steps---
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
```
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. "If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us."

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
```

Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
#############################""",
    """Example 2:
    
Entity_types: ["infrastructure", "building_type", "requirement"]
Text:
```
3.2.1 	Các lối ra được coi là lối ra thoát nạn nếu chúng:
a) Dẫn từ các gian phòng ở tầng 1 ra ngoài theo một trong những cách sau:
- Ra ngoài trực tiếp;
- Qua hành lang;
- Qua tiền sảnh (hay phòng chờ);
- Qua buồng thang bộ;
- Qua hành lang và tiền sảnh (hay phòng chờ);
- Qua hành lang và buồng thang bộ.
b) Dẫn từ các gian phòng của tầng bất kỳ, trừ tầng 1, vào một trong các nơi sau:
- Trực tiếp vào buồng thang bộ hay tới cầu thang bộ loại 3;
- Vào hành lang dẫn trực tiếp vào buồng thang bộ hay tới cầu thang bộ loại 3;
- Vào phòng sử dụng chung (hay phòng chờ) có lối ra trực tiếp dẫn vào buồng thang bộ hoặc tới cầu thang bộ loại 3;
- Vào hành lang bên của nhà có chiều cao PCCC dưới 28 m dẫn trực tiếp vào cầu thang bộ loại 2;
- Ra mái có khai thác sử dụng, hoặc ra một khu vực riêng của mái dẫn tới cầu thang bộ loại 3.
c) Dẫn vào gian phòng liền kề (trừ gian phòng nhóm F5 hạng A hoặc B) trên cùng tầng mà từ gian phòng này có các lối ra như được nêu tại 3.2.1 a, b). Lối ra dẫn vào gian phòng hạng A hoặc B được phép coi là lối ra thoát nạn nếu nó dẫn từ gian phòng kỹ thuật không có người làm việc thường xuyên mà chỉ dùng để phục vụ các gian phòng hạng A hoặc B nêu trên.
d) Các lối ra đáp ứng quy định tại 3.2.2 và các lối ra thoát nạn khác được quy định cụ thể trong quy chuẩn này.
CHÚ THÍCH: 	Trong trường hợp sử dụng cầu thang bộ loại 3 để thoát nạn cần có tính toán thoát nạn phù hợp với Phụ lục G. 
3.2.2 	Các lối ra từ các tầng hầm và tầng nửa hầm, về nguyên tắc, là lối ra thoát nạn khi chúng thoát trực tiếp ra ngoài và được ngăn cách với các buồng thang bộ chung của nhà (xem Hình I.1, Phụ lục I).
Các lối ra sau đây cũng được coi là lối ra thoát nạn:
a) Các lối ra từ các tầng hầm đi qua các buồng thang bộ chung có lối đi riêng ra bên ngoài được ngăn cách với phần còn lại của buồng thang bộ bằng vách đặc ngăn cháy loại 1 (xem Hình I.2, Phụ lục I);
b) Các lối ra từ các tầng hầm và tầng nửa hầm có bố trí các gian phòng hạng C1 đến C4, D, E, đi vào các gian phòng hạng C1 đến C4, D, E và vào tiền sảnh nằm trên tầng một của nhà nhóm F5;
c) Các lối ra từ phòng chờ, phòng gửi đồ, phòng hút thuốc và phòng vệ sinh ở các tầng hầm hoặc tầng nửa hầm của nhà nhóm F2, F3 và F4 đi vào tiền sảnh của tầng 1 theo các cầu thang bộ riêng loại 2. Trong trường hợp này thì phải bảo đảm các yêu cầu sau:
- Tiền sảnh phải được ngăn cách với các hành lang và gian phòng lân cận bằng các vách ngăn cháy không nhỏ hơn loại 1;
- Các gian phòng tầng 1 và các tầng trên phải có đường thoát nạn không đi qua tiền sảnh này (trừ các gian phòng nằm trong tiền sảnh);
- Vật liệu hoàn thiện các phòng chờ, phòng gửi đồ, phòng hút thuốc và phòng vệ sinh ở các tầng hầm hoặc tầng nửa hầm phải thỏa mãn yêu cầu đối với các gian phòng chung theo Phụ lục B;
- Phòng gửi đồ phải có số lối ra thoát nạn thỏa mãn yêu cầu của quy chuẩn này, không tính lối ra thoát nạn theo cầu thang bộ loại 2 nêu trên.
d) Các cửa mở quay có bản lề trên cửa ra vào dành cho phương tiện vận tải đường sắt hoặc đường bộ.
Cho phép bố trí khoang đệm tại lối ra ngoài trực tiếp từ nhà, từ tầng hầm và tầng nửa hầm.
3.2.3 	Các lối ra không được coi là lối ra thoát nạn nếu trên lối ra này có đặt cửa có cánh mở kiểu trượt hoặc xếp, cửa cuốn, cửa quay.
Các cửa đi có cánh mở ra (cửa bản lề) nằm trong các cửa nói trên được coi là lối ra thoát nạn nếu được thiết kế theo đúng yêu cầu quy định.
3.2.4 	Số lượng và chiều rộng của các lối ra thoát nạn từ các gian phòng, các tầng và các nhà được xác định theo số lượng người thoát nạn lớn nhất có thể đi qua chúng và khoảng cách giới hạn cho phép từ chỗ xa nhất có thể có người (sinh hoạt, làm việc) tới lối ra thoát nạn gần nhất. 
CHÚ THÍCH 1: 	Số lượng người thoát nạn lớn nhất từ các không gian khác nhau của nhà hoặc phần nhà được xác định theo G.3, Phụ lục G.
CHÚ THÍCH 2: 	Ngoài các yêu cầu chung được nêu trong quy chuẩn này, yêu cầu cụ thể về số lượng và chiều rộng của các lối ra thoát nạn được nêu trong tài liệu chuẩn cho từng loại công trình. Phụ lục G nêu một số quy định cụ thể cho các nhóm nhà thường gặp.
Các phần nhà có công năng khác nhau và được ngăn chia bởi các bộ phận ngăn cháy thì phải có các lối ra thoát nạn độc lập, trừ các trường hợp được quy định cụ thể trong quy chuẩn này. 
Các phần nhà có công năng khác nhau và được ngăn chia bởi các bộ phận ngăn cháy thành các khoang cháy trong nhà có nhiều công năng phải có các lối ra thoát nạn riêng từ mỗi tầng. Cho phép không quá 50% lối ra thoát nạn dẫn vào khoang cháy lân cận (trừ lối ra thoát nạn dẫn vào khoang cháy nhóm F5). Riêng phần nhà nhóm F5 phải có lối ra thoát nạn riêng.
3.2.5 	Các gian phòng sau phải có không ít hơn hai lối ra thoát nạn:
a) Các gian phòng nhóm F1.1 có mặt đồng thời hơn 15 người;
b) Các gian phòng trong các tầng hầm và tầng nửa hầm có mặt đồng thời hơn 15 người; riêng các gian phòng trong tầng hầm và tầng nửa hầm có từ 6 đến 15 người có mặt đồng thời thì cho phép một trong hai lối ra là lối ra khẩn cấp theo các yêu cầu tại đoạn d) của 3.2.13; 
c) Các gian phòng có mặt đồng thời từ 50 người trở lên;
d) Các gian phòng (trừ các gian phòng nhóm F5) có mặt đồng thời dưới 50 người (bao gồm cả tầng khán giả ở trên cao hoặc ban công khán phòng) với khoảng cách dọc theo lối đi từ chỗ xa nhất có người đến lối ra thoát nạn vượt quá 25 m. Khi có các lối thoát nạn thông vào gian phòng đang xét từ các gian phòng bên cạnh với số lượng trên 5 người có mặt ở mỗi phòng bên cạnh, thì khoảng cách trên phải bao gồm độ dài đường thoát nạn cho người từ các gian phòng bên cạnh đó;
e) Các gian phòng có tổng số người có mặt trong đó và trong các gian liền kề có lối thoát nạn chỉ đi vào gian phòng đang xét từ 50 người trở lên;
f) Các gian phòng nhóm F5 hạng A hoặc B có số người làm việc trong ca đông nhất lớn hơn 5 người, hạng C - khi số người làm việc trong ca đông nhất lớn hơn 25 người hoặc có diện tích lớn hơn 1 000 m2;
g) Các sàn công tác hở và các sàn dành cho người vận hành và bảo dưỡng thiết bị trong các gian phòng nhóm F5 có diện tích lớn hơn 100 m2 - đối với các gian phòng thuộc hạng A và B hoặc lớn hơn 400 m2 - đối với các gian phòng thuộc các hạng khác.
Nếu gian phòng phải có từ 2 lối ra thoát nạn trở lên thì cho phép bố trí không quá 50% số lượng lối ra thoát nạn của gian phòng đó đi qua một gian phòng liền kề, với điều kiện gian phòng liền kề đó cũng phải có lối ra thoát nạn tuân thủ quy định của quy chuẩn này và các tài liệu chuẩn tương ứng cho gian phòng đó.
```

Output:
("entity"::{tuple_delimiter}"Lối ra thoát nạn"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Lối ra thoát nạn là các lối ra từ gian phòng hoặc tầng trong nhà, dẫn đến nơi an toàn bên ngoài khi xảy ra cháy, được quy định rõ trong QCVN 06:2022/BXD."){record_delimiter}
("entity"::{tuple_delimiter}"Lối ra khẩn cấp"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Lối ra khẩn cấp là các lối ra phụ, không được đưa vào tính toán thoát nạn chính thức nhưng giúp tăng cường an toàn khi cháy."){record_delimiter}
("entity"::{tuple_delimiter}"Cầu thang bộ loại 2"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Cầu thang bộ loại 2 là dạng cầu thang bộ chuyên dụng được phép sử dụng thay cho buồng thang bộ trong một số trường hợp đảm bảo an toàn cháy."){record_delimiter}
("entity"::{tuple_delimiter}"Cầu thang bộ loại 3"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Cầu thang bộ loại 3 là dạng cầu thang chuyên dụng được chấp nhận trong các điều kiện thiết kế thoát nạn từ tầng trên, mái hoặc khu vực kỹ thuật."){record_delimiter}
("entity"::{tuple_delimiter}"Buồng thang bộ"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Buồng thang bộ là khu vực cầu thang được sử dụng làm tuyến thoát nạn chính, kết nối các tầng với lối ra ngoài."){record_delimiter}
("entity"::{tuple_delimiter}"Vách ngăn cháy loại 1"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Vách ngăn cháy loại 1 được sử dụng để ngăn cách buồng thang bộ với các lối ra từ tầng hầm nhằm đảm bảo chống cháy lan."){record_delimiter}
("entity"::{tuple_delimiter}"Khoang đệm"::{tuple_delimiter}"infrastructure"::{tuple_delimiter}"Khoang đệm là khu vực đệm tại các lối ra ngoài trực tiếp từ tầng hầm hoặc nhà nhằm ngăn khói và bảo vệ lối thoát nạn."){record_delimiter}
("entity"::{tuple_delimiter}"Nhà nhóm F5"::{tuple_delimiter}"building_type"::{tuple_delimiter}"Nhà nhóm F5 là loại công trình có công năng đặc biệt, yêu cầu lối ra thoát nạn riêng biệt."){record_delimiter}
("entity"::{tuple_delimiter}"Yêu cầu số lượng lối ra"::{tuple_delimiter}"requirement"::{tuple_delimiter}"Số lượng lối ra thoát nạn tối thiểu được xác định dựa trên số lượng người sử dụng không gian, chức năng công năng và tầng nhà."){record_delimiter}
("entity"::{tuple_delimiter}"Yêu cầu chiều rộng lối ra"::{tuple_delimiter}"requirement"::{tuple_delimiter}"Chiều rộng tối thiểu của lối ra thoát nạn được quy định dựa trên loại không gian, số người thoát nạn và chiều cao nhà."){record_delimiter}
("relationship"::{tuple_delimiter}"Lối ra thoát nạn"::{tuple_delimiter}"Cầu thang bộ loại 3"::{tuple_delimiter}"Lối ra thoát nạn có thể dẫn trực tiếp đến cầu thang bộ loại 3 trong các tầng trên hoặc khu vực mái."::{tuple_delimiter}"tuyến thoát nạn, kết nối tầng"::{tuple_delimiter}8){record_delimiter}
("relationship"::{tuple_delimiter}"Lối ra từ tầng hầm"::{tuple_delimiter}"Vách ngăn cháy loại 1"::{tuple_delimiter}"Lối ra từ tầng hầm đi qua buồng thang bộ chung phải được ngăn cách bằng vách ngăn cháy loại 1 để đảm bảo an toàn cháy."::{tuple_delimiter}"chống cháy lan, ngăn cách an toàn"::{tuple_delimiter}9){record_delimiter}
("relationship"::{tuple_delimiter}"Lối ra thoát nạn"::{tuple_delimiter}"Khoang đệm"::{tuple_delimiter}"Cho phép bố trí khoang đệm tại các lối ra ngoài trực tiếp để tăng cường ngăn khói và bảo vệ người di chuyển thoát nạn."::{tuple_delimiter}"ngăn khói, bảo vệ tuyến thoát hiểm"::{tuple_delimiter}7){record_delimiter}
("relationship"::{tuple_delimiter}"Yêu cầu số lượng lối ra"::{tuple_delimiter}"Số người trong gian phòng"::{tuple_delimiter}"Số lượng lối ra thoát nạn yêu cầu được xác định theo tổng số người có mặt đồng thời trong gian phòng."::{tuple_delimiter}"yêu cầu thiết kế, an toàn thoát hiểm"::{tuple_delimiter}9){record_delimiter}
("relationship"::{tuple_delimiter}"Nhà nhóm F5"::{tuple_delimiter}"Lối ra thoát nạn riêng"::{tuple_delimiter}"Nhà nhóm F5 yêu cầu các lối ra thoát nạn riêng biệt, không được chia sẻ với phần nhà khác."::{tuple_delimiter}"bố trí riêng biệt, an toàn công năng đặc biệt"::{tuple_delimiter}8){record_delimiter}
("content_keywords"::{tuple_delimiter}"lối ra thoát nạn, lối ra khẩn cấp, cầu thang bộ, khoang đệm, vách ngăn cháy, yêu cầu số lượng lối ra, quy định chiều rộng lối ra"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: ["fire_resistance_level", "hazard_class", "hazard_level", "volume_threshold", "flow_rate"]
Text:
```
Bậc chịu lửa I, II

    Hạng A, B, C

        Cấp nguy hiểm S0, S1

            ≤150 m³: 2 × 2.5 L/s

                150 m³: 3 × 2.5 L/s

    Hạng D, E

        Không quy định cấp nguy hiểm kết cấu

            ≤150 m³: 1 × 2.5 L/s

                150 m³: 1 × 2.5 L/s

Bậc chịu lửa III

    Hạng A, B, C

        Cấp nguy hiểm S0

            ≤150 m³: 2 × 2.5 L/s

                150 m³: 3 × 2.5 L/s

    Hạng D, E

        Cấp nguy hiểm S0, S1

            ≤150 m³: 1 × 2.5 L/s

                150 m³: 2 × 2.5 L/s

Bậc chịu lửa IV

    Hạng A, B

        Cấp nguy hiểm S0

            ≤150 m³: 2 × 2.5 L/s

                150 m³: 3 × 2.5 L/s

    Hạng C

        Cấp nguy hiểm S0, S1

            ≤150 m³: 2 × 2.5 L/s

                150 m³: 2 × 5 L/s

        Cấp nguy hiểm S2, S3

            ≤150 m³: 3 × 2.5 L/s

                150 m³: 4 × 2.5 L/s

    Hạng D, E

        Cấp nguy hiểm S0, S1, S2, S3

            ≤150 m³: 1 × 2.5 L/s

                150 m³: 2 × 2.5 L/s

Bậc chịu lửa V

    Hạng C

        Không quy định cấp nguy hiểm kết cấu

            ≤150 m³: 2 × 2.5 L/s

                150 m³: 2 × 5 L/s

    Hạng D, E

        Không quy định cấp nguy hiểm kết cấu

            ≤150 m³: 1 × 2.5 L/s

                150 m³: 2 × 2.5 L/s
```

Output:
("entity"::{tuple_delimiter}"Bậc chịu lửa I, II"::{tuple_delimiter}"fire_resistance_level"::{tuple_delimiter}"Bậc chịu lửa I, II là cấp độ chịu lửa cao nhất, yêu cầu các tiêu chuẩn nghiêm ngặt về khả năng chống cháy cho kết cấu công trình."){record_delimiter}
("entity"::{tuple_delimiter}"Bậc chịu lửa III"::{tuple_delimiter}"fire_resistance_level"::{tuple_delimiter}"Bậc chịu lửa III là cấp độ chịu lửa trung bình, áp dụng cho công trình có yêu cầu chống cháy tiêu chuẩn."){record_delimiter}
("entity"::{tuple_delimiter}"Bậc chịu lửa IV"::{tuple_delimiter}"fire_resistance_level"::{tuple_delimiter}"Bậc chịu lửa IV là cấp chịu lửa thấp hơn, áp dụng cho công trình có nguy cơ cháy trung bình."){record_delimiter}
("entity"::{tuple_delimiter}"Bậc chịu lửa V"::{tuple_delimiter}"fire_resistance_level"::{tuple_delimiter}"Bậc chịu lửa V là cấp chịu lửa thấp nhất, áp dụng cho công trình nhỏ và ít nguy cơ cháy."){record_delimiter}
("entity"::{tuple_delimiter}"Hạng A, B, C"::{tuple_delimiter}"hazard_class"::{tuple_delimiter}"Hạng A, B, C là phân loại nguy hiểm cháy cao, yêu cầu tiêu chuẩn chữa cháy nghiêm ngặt."){record_delimiter}
("entity"::{tuple_delimiter}"Hạng D, E"::{tuple_delimiter}"hazard_class"::{tuple_delimiter}"Hạng D, E là phân loại nguy hiểm cháy thấp, áp dụng cho các công trình có nguy cơ cháy thấp hơn."){record_delimiter}
("entity"::{tuple_delimiter}"Hạng C"::{tuple_delimiter}"hazard_class"::{tuple_delimiter}"Hạng C là phân loại trung gian giữa nhóm nguy hiểm cao và thấp."){record_delimiter}
("entity"::{tuple_delimiter}"Cấp nguy hiểm S0, S1, S2, S3"::{tuple_delimiter}"hazard_level"::{tuple_delimiter}"Cấp nguy hiểm S0, S1, S2, S3 là các mức độ nguy hiểm kết cấu, với S0 là nguy hiểm thấp nhất và S3 là cao nhất."){record_delimiter}
("entity"::{tuple_delimiter}"≤150 m³"::{tuple_delimiter}"volume_threshold"::{tuple_delimiter}"Thể tích không gian nhỏ hơn hoặc bằng 150 m³ được sử dụng làm ngưỡng áp dụng yêu cầu lưu lượng chữa cháy."){record_delimiter}
("entity"::{tuple_delimiter}"150 m³"::{tuple_delimiter}"volume_threshold"::{tuple_delimiter}"Thể tích không gian lớn hơn 150 m³ được dùng để áp dụng yêu cầu lưu lượng chữa cháy cao hơn."){record_delimiter}
("entity"::{tuple_delimiter}"2 × 2.5 L/s"::{tuple_delimiter}"flow_rate"::{tuple_delimiter}"Yêu cầu cung cấp 2 vòi chữa cháy, mỗi vòi 2.5 lít mỗi giây."){record_delimiter}
("entity"::{tuple_delimiter}"3 × 2.5 L/s"::{tuple_delimiter}"flow_rate"::{tuple_delimiter}"Yêu cầu cung cấp 3 vòi chữa cháy, mỗi vòi 2.5 lít mỗi giây."){record_delimiter}
("entity"::{tuple_delimiter}"2 × 5 L/s"::{tuple_delimiter}"flow_rate"::{tuple_delimiter}"Yêu cầu cung cấp 2 vòi chữa cháy, mỗi vòi 5 lít mỗi giây."){record_delimiter}
("entity"::{tuple_delimiter}"4 × 2.5 L/s"::{tuple_delimiter}"flow_rate"::{tuple_delimiter}"Yêu cầu cung cấp 4 vòi chữa cháy, mỗi vòi 2.5 lít mỗi giây."){record_delimiter}
("relationship"::{tuple_delimiter}"Bậc chịu lửa I, II"::{tuple_delimiter}"≤150 m³"::{tuple_delimiter}"Đối với bậc chịu lửa I, II và thể tích nhỏ hơn hoặc bằng 150 m³, áp dụng các yêu cầu lưu lượng theo phân hạng và cấp nguy hiểm."::{tuple_delimiter}"quy chuẩn chữa cháy, phân loại thể tích"::{tuple_delimiter}9){record_delimiter}
("relationship"::{tuple_delimiter}"Cấp nguy hiểm S0, S1"::{tuple_delimiter}"2 × 2.5 L/s"::{tuple_delimiter}"Cấp nguy hiểm S0, S1 yêu cầu sử dụng 2 vòi chữa cháy 2.5 L/s cho không gian ≤150 m³."::{tuple_delimiter}"yêu cầu kỹ thuật, lưu lượng nước"::{tuple_delimiter}8){record_delimiter}
("relationship"::{tuple_delimiter}"Cấp nguy hiểm S0, S1"::{tuple_delimiter}"3 × 2.5 L/s"::{tuple_delimiter}"Cấp nguy hiểm S0, S1 yêu cầu sử dụng 3 vòi chữa cháy 2.5 L/s khi thể tích >150 m³."::{tuple_delimiter}"tăng lưu lượng, phân loại nguy hiểm"::{tuple_delimiter}8){record_delimiter}
("relationship"::{tuple_delimiter}"Hạng D, E"::{tuple_delimiter}"≤150 m³"::{tuple_delimiter}"Hạng D, E áp dụng yêu cầu 1 × 2.5 L/s khi thể tích nhỏ hơn hoặc bằng 150 m³."::{tuple_delimiter}"nguy hiểm thấp, yêu cầu cơ bản"::{tuple_delimiter}7){record_delimiter}
("relationship"::{tuple_delimiter}"Hạng D, E"::{tuple_delimiter}"150 m³"::{tuple_delimiter}"Khi thể tích lớn hơn 150 m³, Hạng D, E yêu cầu 2 × 2.5 L/s."::{tuple_delimiter}"yêu cầu tăng cường, lưu lượng nước"::{tuple_delimiter}7){record_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user query about Knowledge Graph and Document Chunks provided in JSON format below.


---Goal---

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Graph and Document Chunks---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Document Chunks (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base.
- Addtional user prompt: {user_prompt}

Response:"""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query and conversation history.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Consider both the current query and relevant conversation history when extracting keywords
- Output the keywords in JSON format, it will be parsed by a JSON parser, do not add any extra content in output
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes
  - "low_level_keywords" for specific entities or details

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
#############################""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
#############################""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
#############################""",
]

PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided provided in JSON format below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks(DC)---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating each source from Document Chunks(DC), and include the file path if available, in the following format: [DC] file_path
- If you don't know the answer, just say so.
- Do not include information not provided by the Document Chunks.
- Addtional user prompt: {user_prompt}

Response:"""

# TODO: deprecated
PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar, and whether the answer to Question 2 can be used to answer Question 1, provide a similarity score between 0 and 1 directly.

Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""
