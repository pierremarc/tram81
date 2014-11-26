@background-color: #fff;
@grey: #bbb;
@white: #fff;

@green: #e8f3e8;

#zone {line-color:#996600; opacity:0.3;}
  
//ROADS VARIABLES
@road-fill : @background-color; 
@roads: @grey;
@primary: 6;
@secondary: 4;
@tertiary: 2;
@small-roads: 1;

//WATER VARIABLES
@water : #e4e9f4;

//LABELS VARIABLES
@road-label : 'Crimson Text Semibold';
@road-label-color : (@grey - 70%);
@place-label : 'Crimson Text Bold';
@place-label-color : (@grey - 100%);
@water-label : 'Crimson Text Roman';


Map {
  background-color: @white;
  buffer-size: 256;
}

#countries {
  ::outline {
    line-color: (#85c5d3 + 50%);
    line-width: 2;
    line-join: round;
  }
  polygon-fill: @background-color;
  line-color:red;
}


