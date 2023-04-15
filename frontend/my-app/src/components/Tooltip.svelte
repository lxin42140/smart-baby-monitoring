<script>
	import Tooltip, { Wrapper } from '@smui/tooltip';
	import IconButton, { Icon }from '@smui/icon-button';
	import { mdiInformation } from '@mdi/js';
  import { Svg } from '@smui/common';

  export let message;
</script>

<Wrapper>
	<!-- <span tabindex="0" role="button">I'm a span element.</span> -->
	<!--
      For tooltips on things that don't have a
      visually declared boundary, like plain text,
      use the `unbounded` prop to remove the gap
      between the element and the tooltip.
    -->
	<div style="display: flex; align-items: center;">
		<IconButton size="button">
			<Icon component={Svg} viewBox="0 0 24 24">
				<path fill="currentColor" d={mdiInformation} />
			</Icon>
		</IconButton>
	</div>
	<Tooltip unbounded xPos="center" yPos="above">{message}</Tooltip>
</Wrapper>
