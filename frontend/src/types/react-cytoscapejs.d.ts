declare module "react-cytoscapejs" {
  import type cytoscape from "cytoscape";
  import type { Component } from "react";

  interface CytoscapeComponentProps {
    elements: cytoscape.ElementDefinition[];
    stylesheet?: cytoscape.StylesheetStyle[];
    layout?: cytoscape.LayoutOptions;
    style?: React.CSSProperties;
    cy?: (cy: cytoscape.Core) => void;
    [key: string]: unknown;
  }

  export default class CytoscapeComponent extends Component<CytoscapeComponentProps> {}
}
