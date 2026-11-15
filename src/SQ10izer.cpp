// SQ10izer: 16 steps of small, unquantised pitch offsets (up to +-30 cents),
// added to a V/OCT signal on each clock. Gives a quantised sequencer the
// slightly-off, hand-dialled tuning of an early analogue step sequencer.
#include "plugin.hpp"

// ---- LAYOUT (same numbers in res/make_panel.py) ----
static const float STEP_X0 = 10.55f, STEP_DX = 11.5f;
static const float ROW_Y[2] = {28.0f, 50.0f};
static const float LIGHT_DY = 6.6f;
static const float X_STRENGTH = 38.0f, X_LENGTH = 14.0f, X_RAND = 62.0f, X_CLOCK = 87.0f;
static const float CTRL_Y = 75.0f, CV_Y = 92.0f;
static const float BOT_Y = 113.0f;
static const float X_IN = 14.0f, X_OFFSET = 60.0f, X_OUT = 86.0f;

static const int NUM_STEPS = 16;
static const float MAX_CENTS = 30.f;

struct SQ10izer : Module {
	enum ParamIds {
		ENUMS(STEP_PARAM, NUM_STEPS),
		STRENGTH_PARAM,
		LENGTH_PARAM,
		RAND_PARAM,
		NUM_PARAMS
	};
	enum InputIds {
		CLOCK_INPUT,
		RESET_INPUT,
		RAND_INPUT,
		STRENGTH_INPUT,
		LENGTH_INPUT,
		VOCT_INPUT,
		NUM_INPUTS
	};
	enum OutputIds {
		VOCT_OUTPUT,
		OFFSET_OUTPUT,
		NUM_OUTPUTS
	};
	enum LightIds {
		ENUMS(STEP_LIGHT, NUM_STEPS),
		RAND_LIGHT,
		NUM_LIGHTS
	};

	dsp::SchmittTrigger clockTrigger, resetTrigger, randTrigger, randButtonTrigger;
	dsp::PulseGenerator resetBlank;   // ignore clocks for 1 ms after a reset
	dsp::PulseGenerator randFlash;
	dsp::ClockDivider lightDivider;

	int step = -1;          // -1 = just reset: the next clock plays step 1
	bool gentle = false;    // right-click: random values mostly small
	bool randInLoop = false; // right-click: RANDOMISE only changes the steps in the loop

	SQ10izer() {
		config(NUM_PARAMS, NUM_INPUTS, NUM_OUTPUTS, NUM_LIGHTS);
		for (int i = 0; i < NUM_STEPS; i++) {
			configParam(STEP_PARAM + i, -MAX_CENTS, MAX_CENTS, 0.f, string::f("Step %d", i + 1), " cents");
		}
		configParam(STRENGTH_PARAM, 0.f, MAX_CENTS, 15.f, "Random strength (furthest a random step can land)", " cents");
		configParam(LENGTH_PARAM, 1.f, 16.f, 16.f, "Length", " steps");
		getParamQuantity(LENGTH_PARAM)->snapEnabled = true;
		getParamQuantity(STRENGTH_PARAM)->randomizeEnabled = false;
		getParamQuantity(LENGTH_PARAM)->randomizeEnabled = false;
		configButton(RAND_PARAM, "Randomise the steps");

		configInput(CLOCK_INPUT, "Clock");
		configInput(RESET_INPUT, "Reset");
		configInput(RAND_INPUT, "Randomise trigger");
		configInput(STRENGTH_INPUT, "Random strength CV (+1 V = +3 cents)");
		configInput(LENGTH_INPUT, "Length CV (+1 V = +1.5 steps)");
		configInput(VOCT_INPUT, "V/OCT");
		configOutput(VOCT_OUTPUT, "V/OCT plus step offset");
		configOutput(OFFSET_OUTPUT, "Step offset on its own");
		configBypass(VOCT_INPUT, VOCT_OUTPUT);
		for (int i = 0; i < NUM_STEPS; i++)
			configLight(STEP_LIGHT + i, string::f("Step %d", i + 1));

		lightDivider.setDivision(64);
	}

	float strengthCents() {
		float s = params[STRENGTH_PARAM].getValue() + inputs[STRENGTH_INPUT].getVoltage() * 3.f;
		return clamp(s, 0.f, MAX_CENTS);
	}

	int length() {
		float l = params[LENGTH_PARAM].getValue() + inputs[LENGTH_INPUT].getVoltage() * 1.5f;
		return clamp((int) std::round(l), 1, NUM_STEPS);
	}

	// A random offset in cents, no further than STRENGTH from in tune.
	float randomValue() {
		float s = strengthCents();
		if (gentle) {
			// bell-shaped: most steps a little off, now and then one further out
			return clamp(random::normal() * 0.35f * s, -s, s);
		}
		return (random::uniform() * 2.f - 1.f) * s;
	}

	void randomiseSteps() {
		int n = randInLoop ? length() : NUM_STEPS;
		for (int i = 0; i < n; i++)
			params[STEP_PARAM + i].setValue(randomValue());
		randFlash.trigger(0.15f);
	}

	void onReset() override {
		step = -1;
	}

	void onRandomize() override {
		Module::onRandomize();
		step = -1;
	}

	void process(const ProcessArgs& args) override {
		if (resetTrigger.process(inputs[RESET_INPUT].getVoltage(), 0.1f, 1.f)) {
			step = -1;
			resetBlank.trigger(1e-3f);
		}
		bool blanked = resetBlank.process(args.sampleTime);

		int len = length();
		if (clockTrigger.process(inputs[CLOCK_INPUT].getVoltage(), 0.1f, 1.f) && !blanked) {
			step++;
			if (step >= len)
				step = 0;
		}
		// LENGTH turned down below the playing step: jump back into the loop
		if (step >= len)
			step = 0;

		bool rb = randButtonTrigger.process(params[RAND_PARAM].getValue());
		bool rt = randTrigger.process(inputs[RAND_INPUT].getVoltage(), 0.1f, 1.f);
		if (rb || rt)
			randomiseSteps();

		int playing = step < 0 ? 0 : step;
		float offset = params[STEP_PARAM + playing].getValue() / 1200.f;

		int channels = std::max(1, inputs[VOCT_INPUT].getChannels());
		outputs[VOCT_OUTPUT].setChannels(channels);
		for (int c = 0; c < channels; c++)
			outputs[VOCT_OUTPUT].setVoltage(inputs[VOCT_INPUT].getVoltage(c) + offset, c);
		outputs[OFFSET_OUTPUT].setVoltage(offset);

		bool flash = randFlash.process(args.sampleTime);
		if (lightDivider.process()) {
			float dt = args.sampleTime * lightDivider.getDivision();
			for (int i = 0; i < NUM_STEPS; i++) {
				float b = (i == playing) ? 1.f : (i < len ? 0.12f : 0.f);
				lights[STEP_LIGHT + i].setBrightnessSmooth(b, dt, 30.f);
			}
			lights[RAND_LIGHT].setBrightnessSmooth(flash || params[RAND_PARAM].getValue() > 0.f ? 1.f : 0.f, dt, 30.f);
		}
	}

	json_t* dataToJson() override {
		json_t* root = json_object();
		json_object_set_new(root, "gentle", json_boolean(gentle));
		json_object_set_new(root, "randInLoop", json_boolean(randInLoop));
		json_object_set_new(root, "step", json_integer(step));
		return root;
	}

	void dataFromJson(json_t* root) override {
		json_t* j;
		if ((j = json_object_get(root, "gentle"))) gentle = json_boolean_value(j);
		if ((j = json_object_get(root, "randInLoop"))) randInLoop = json_boolean_value(j);
		if ((j = json_object_get(root, "step"))) step = clamp((int) json_integer_value(j), -1, NUM_STEPS - 1);
	}
};

struct SQ10izerWidget : ModuleWidget {
	SQ10izerWidget(SQ10izer* module) {
		setModule(module);
		setPanel(createPanel(asset::plugin(pluginInstance, "res/SQ10izer.svg")));

		addChild(createWidget<ScrewSilver>(Vec(RACK_GRID_WIDTH, 0)));
		addChild(createWidget<ScrewSilver>(Vec(box.size.x - 2 * RACK_GRID_WIDTH, 0)));
		addChild(createWidget<ScrewSilver>(Vec(RACK_GRID_WIDTH, RACK_GRID_HEIGHT - RACK_GRID_WIDTH)));
		addChild(createWidget<ScrewSilver>(Vec(box.size.x - 2 * RACK_GRID_WIDTH, RACK_GRID_HEIGHT - RACK_GRID_WIDTH)));

		for (int i = 0; i < NUM_STEPS; i++) {
			float x = STEP_X0 + (i % 8) * STEP_DX;
			float y = ROW_Y[i / 8];
			addParam(createParamCentered<RoundSmallBlackKnob>(mm2px(Vec(x, y)), module, SQ10izer::STEP_PARAM + i));
			addChild(createLightCentered<SmallLight<YellowLight>>(mm2px(Vec(x, y + LIGHT_DY)), module, SQ10izer::STEP_LIGHT + i));
		}

		addParam(createParamCentered<RoundBlackKnob>(mm2px(Vec(X_STRENGTH, CTRL_Y)), module, SQ10izer::STRENGTH_PARAM));
		addParam(createParamCentered<RoundBlackSnapKnob>(mm2px(Vec(X_LENGTH, CTRL_Y)), module, SQ10izer::LENGTH_PARAM));
		addParam(createLightParamCentered<VCVLightBezel<YellowLight>>(mm2px(Vec(X_RAND, CTRL_Y)), module, SQ10izer::RAND_PARAM, SQ10izer::RAND_LIGHT));
		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_CLOCK, CTRL_Y)), module, SQ10izer::CLOCK_INPUT));

		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_STRENGTH, CV_Y)), module, SQ10izer::STRENGTH_INPUT));
		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_LENGTH, CV_Y)), module, SQ10izer::LENGTH_INPUT));
		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_RAND, CV_Y)), module, SQ10izer::RAND_INPUT));
		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_CLOCK, CV_Y)), module, SQ10izer::RESET_INPUT));

		addInput(createInputCentered<PJ301MPort>(mm2px(Vec(X_IN, BOT_Y)), module, SQ10izer::VOCT_INPUT));
		addOutput(createOutputCentered<PJ301MPort>(mm2px(Vec(X_OFFSET, BOT_Y)), module, SQ10izer::OFFSET_OUTPUT));
		addOutput(createOutputCentered<PJ301MPort>(mm2px(Vec(X_OUT, BOT_Y)), module, SQ10izer::VOCT_OUTPUT));
	}

	void appendContextMenu(Menu* menu) override {
		SQ10izer* module = dynamic_cast<SQ10izer*>(this->module);
		if (!module)
			return;
		menu->addChild(new MenuSeparator);
		menu->addChild(createBoolPtrMenuItem("Gentle random (mostly small offsets)", "", &module->gentle));
		menu->addChild(createBoolPtrMenuItem("RANDOMISE only changes steps inside LENGTH", "", &module->randInLoop));
		menu->addChild(createMenuItem("Zero all steps", "", [=]() {
			for (int i = 0; i < NUM_STEPS; i++)
				module->params[SQ10izer::STEP_PARAM + i].setValue(0.f);
		}));
	}
};

Model* modelSQ10izer = createModel<SQ10izer, SQ10izerWidget>("SQ10izer");
