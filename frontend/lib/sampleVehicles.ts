import type {Vehicle} from "./types";

const base={mileage_km:0,transmission:"Automatic",fuel_type:"Petrol",condition:"Sample presentation only",location:"Dealer location",description:"Example content used only to preview the website before real inventory is published.",features:[],known_issues:"",seller_history:"",video_url:"",publication_status:"published" as const,availability:"available" as const,is_featured:true,version:1,published_at:null,created_at:"",updated_at:""};

export const sampleVehicles:Vehicle[]=[
  {...base,id:"sample-lexus",slug:"sample-lexus",title:"2022 Lexus RX 350",make:"Lexus",model:"RX 350",year:2022,price:"0",images:[{id:-1,url:"/sample-vehicles/lexus-rx.jpg",alt_text:"Sample Lexus presentation photograph",position:0}]},
  {...base,id:"sample-mercedes",slug:"sample-mercedes",title:"2021 Mercedes-Benz GLE 450",make:"Mercedes-Benz",model:"GLE 450",year:2021,price:"0",images:[{id:-2,url:"/sample-vehicles/mercedes-gle.jpg",alt_text:"Sample Mercedes-Benz presentation photograph",position:0}]},
  {...base,id:"sample-toyota",slug:"sample-toyota",title:"2020 Toyota Land Cruiser Prado",make:"Toyota",model:"Land Cruiser Prado",year:2020,price:"0",is_featured:false,images:[{id:-3,url:"/sample-vehicles/toyota-prado.jpg",alt_text:"Sample Toyota presentation photograph",position:0}]},
  {...base,id:"sample-porsche",slug:"sample-porsche",title:"2019 Porsche Macan S",make:"Porsche",model:"Macan S",year:2019,price:"0",is_featured:false,images:[{id:-4,url:"/sample-vehicles/porsche-macan.jpg",alt_text:"Sample Porsche presentation photograph",position:0}]},
];
export const isSampleVehicle=(vehicle:Vehicle)=>vehicle.id.startsWith("sample-");
