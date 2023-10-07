
let directions = {
	"forward": false,
	"backward": false,
	"turn_left": false,
	"turn_right": false
}

const CANVAS_WIDTH = 320;
const CANVAS_HEIGHT = 320;
let canvas: HTMLCanvasElement | null = null;
let ctx: CanvasRenderingContext2D | null = null;
let speed_field: HTMLLabelElement | null = null;
let obstacle_field: HTMLLabelElement | null = null;
let connect_btn: HTMLButtonElement | null = null;
let websocket: WebSocket | null = null;
let ip_port_value = "localhost:8000"

interface recv_data {
	image: Array<number>;
	speed: number;
	obstacle: Array<[number, number]>;
}

function update_canvas(data: recv_data) {
	if(ctx) {
		let palette = ctx.getImageData(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT); 
		palette.data.set(new Uint8ClampedArray(data.image));
		ctx.putImageData(palette, 0, 0);
	}
	else {
		console.log("Cannot update canvas because it is not setup.");
	}
}

function update_fields(data: recv_data) {
	if(speed_field && obstacle_field) {
		speed_field.innerHTML = `Current Speed: ${data.speed}`;
		obstacle_field.innerHTML = `Obstacles: ${data.obstacle}`
	}
}

function update(data: recv_data) {
	update_canvas(data);
	update_fields(data);
}

const keychange = (e: KeyboardEvent) => {
	const prev_directions = JSON.parse(JSON.stringify(directions));
	let change = e.type === "keydown";
	if(websocket) {
		switch (e.key) {
			case 'a':
				directions["turn_left"] = change;
				break;
			case 'd':
				directions["turn_right"] = change;
				break;
			case 'w':
				directions["forward"] = change;
				break;
			case 's':
				directions["backward"] = change;
				break;
		}
		if(JSON.stringify(prev_directions) !== JSON.stringify(directions)) {
			console.log(`Sending direction change: ${JSON.stringify(directions)}`);
			websocket.send(JSON.stringify(directions));
		}
	}
};

function create_websocket(ip_port: String) {
	let ws = new WebSocket(`ws://${ip_port}`);
	ws.onerror = (e: Event) => {
		console.log(`Websocket Failed: ${e}`);
	};
	ws.onopen = (e: Event) => {
		console.log("Sending Setup Message");
		ws.send(JSON.stringify(directions));
	}
	ws.onmessage = (ev: MessageEvent<any>) => {
		const decoded_data: recv_data = JSON.parse(ev.data);
		update(decoded_data)
	}
	return ws;
}

window.onload = () => {
	connect_btn = document.getElementById("ip_port_btn_id") as HTMLButtonElement;
	canvas = document.getElementById("image_id") as HTMLCanvasElement;
	ctx = canvas.getContext("2d");
	speed_field = document.getElementById("speed_id") as HTMLLabelElement;
	obstacle_field = document.getElementById("obstacles_id") as HTMLLabelElement;

	window.addEventListener("keydown", keychange);
	window.addEventListener("keyup", keychange);

	if(connect_btn) {
		connect_btn.onclick = (e: MouseEvent) => {
			const new_ip_port_value = (document.getElementById("ip_port_id") as HTMLInputElement).value;
			if(new_ip_port_value) {
				ip_port_value = new_ip_port_value;
			}
			console.log("Connecting To: ", ip_port_value);
			websocket = create_websocket(ip_port_value);
		}
	}
}